import socket
from _thread import *
import threading
import json
import time

# Mutex to control access to the queue
queueMutex = threading.Lock()

# Queue
queue = []

# Mutex to control access to the load balanced servers list
lbServerMutex = threading.Lock()

# Mutex for sending data
sendMutex = threading.Lock()

# Mutex to control print access
printLock = threading.Lock()

# Server loads
loadThreads = []

connectedClients = 0    # Number of client currently connected to load balancer

LOCALHOST = ""
LB_PORT = 4000
CLIENT_PORT = 8081  # Port clients communicate with load balancer on
ALLOWED_CLIENTS = 5     # Number of clients load balancer will handle at a time


currentClients = 0
currentClientsMutex = threading.Lock()

def currentClientsCallback():
  global currentClients
  global currentClientsMutex

  currentClientsMutex.acquire()
  try:
    currentClients -= 1
    print("LB[dec] Number of clients connected to LB: %d" % currentClients)
  finally:
    currentClientsMutex.release()


class LB_Server:
  def __init__(self, ip, port, load):
    self.ip = ip
    self.port = port
    self.load = load


class Client:
  def __init__(self, priority, message, thread):
    self.priority = priority
    self.message = message
    self.thread = thread


def determineLowestLoad():
  lowest = 100
  l = LB_Server('127.0.0.1', LB_PORT, 100)
  success = False
  lbServerMutex.acquire()
  try:
    for loadThread in loadThreads:
      if (loadThread.load < lowest):
        lowest = loadThread.load
        l = loadThread
        success = True
  finally:
    lbServerMutex.release()
  return (l, success)


def determineLowestPriority():
  lowest = 100
  c = Client('100', '', threading.Thread)
  success = False
  for client in queue:
    if (int(client.priority) < lowest):
      lowest = int(client.priority)
      c = client
      success = True
  return (c, success)


# Spawn thread that monitors the queue
class QueueThread(threading.Thread):
  def run(self):
    while (True):
      if (True): # if I have open hosts
        queueMutex.acquire()
        try:
          (client, success1) = determineLowestPriority()
          (lbServer, success2) = determineLowestLoad()
          if (success1 and success2):
            client.thread.redirAddr = lbServer.ip
            client.thread.redirPort = lbServer.port
            client.thread.redir = True
            queue.remove(client)
        finally:
          queueMutex.release()
      time.sleep(0.001)


# Spawn thread that monitors the load of an individual server
class LoadThread(threading.Thread):
  def __init__(self, sock):
    threading.Thread.__init__(self)
    #self.threadSafePrint("LB: Listening for servers on " + str(LOCALHOST) + ":" + str(LB_PORT))
    print("LB LT Listening", flush=True)
    self.load = 0
    self.ip = ""
    self.port = 4001
    self.socket = sock
    self.loadAverage = 0
    self.n = 1

  def run(self):
    while (True):
      #print("Going to ask for load values", flush=True)
      connectMsg = '{ \
                      "message": "Hey I need your load values" \
                    }'
      self.socket.sendall(bytes(connectMsg, 'UTF-8'))
      #print("Waiting for response", flush=True)
      dataRecv = self.socket.recv(1024).decode()
      #print("RECEIVED: %s" % dataRecv)

      dataRecvJson = json.loads(dataRecv)
      #print("Received: %s" % (dataRecvJson), flush=True)
      if (self.load != dataRecvJson['load']):
        print("DIFF Received: %s" % (dataRecvJson), flush=True)

      self.load = dataRecvJson['load']
      self.port = dataRecvJson['port']
      self.ip = dataRecvJson['ip']
        
      fname = "serverLoad_"+str(self.port)

      self.loadAverage = ((float(self.loadAverage)*float(self.n)) + float(self.load)) / (float(self.n+1))
      self.n += 1
      
      f=open(fname, "a+")
      f.write(str(self.loadAverage)+"\n")
      f.close()
      time.sleep(0.001)

    self.socket.close()


# Spawn thread that receives input from load balanced servers and spawns a thread to monitor them
class MasterLoadThread(threading.Thread):
  def __init__(self):
    threading.Thread.__init__(self)
    self.reqSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.reqSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    self.reqSocket.bind((LOCALHOST, LB_PORT))
    self.threadSafePrint("LB: Listening for servers on " + str(LOCALHOST) + ":" + str(LB_PORT))

  def threadSafePrint(self, msg):
    print(msg, flush=True)
    #printLock.acquire()
    #print(msg)
    #printLock.release()

  def run(self):
    global loadThreads

    self.reqSocket.listen(1)

    while (True):
      self.serverSock, self.serverAddr = self.reqSocket.accept()
      self.threadSafePrint("LB: Server connected to load balancer: " + str(self.serverAddr[0]) + ":" + str(self.serverAddr[1]))
      #thread = threading.Thread(target=self.pingServer, args=(self.serverSock,))
      #thread.start()
      loadThread = LoadThread(self.serverSock)
      loadThread.start()
      loadThreads.append(loadThread)


#def strToClient(message, thread):
#  messageJson = json.loads(message)


#def strToClient(message, thread):
#  messageJson = json.loads(message)
#  print("message json", flush=True)
#  print(messageJson, flush=True)
#  return Client(messageJson["priority"], messageJson["message"], thread)

def printClient(m):
  print("(%d) %s;" % (m.priority, m.message), end='', flush=True)
  print(" Thread: ", end='', flush=True)
  print(m.thread, flush=True)


# Spawns threads to handle Client connections
class ClientThread(threading.Thread):
  def __init__(self, sock, callback=lambda: None):
    threading.Thread.__init__(self)
    print("ClientThread listening", flush=True)
    self.commSock = sock
    self.priority = 0
    self.callback = callback
    self.redir = False
    self.redirAddr = ""
    self.redirPort = 0

  def run(self):
    global queueMutex
    global queue

    data = self.commSock.recv(1024)
    if not data:
      print('LB: Closing connection to client', flush=True)
    #print("RECEIVED: %s" % (data.decode()))
    dataJson = json.loads(data.decode())
    self.priority = dataJson['priority']
    queueMutex.acquire()
    try:
      c = Client(str(self.priority), "", self)
      queue.append(c)
    finally:
      queueMutex.release()

    while (True):
      if (self.redir == True):
        sendMutex.acquire()
        redirMessage = '{ \
                          "status": 200, \
                          "ip": "' + self.redirAddr + '", \
                          "port": ' + str(self.redirPort) + ' \
                        }'
        #print("GOING TO SEND")
        #print(redirMessage)
        self.commSock.send(bytes(redirMessage, 'utf-8'))
        sendMutex.release()
        break
    self.commSock.close()
    self.callback()


# Spawns threads to handle Client connections
class MasterClientThread(threading.Thread):
  def __init__(self):
    threading.Thread.__init__(self)
    self.reqSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.reqSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    self.reqSocket.bind((LOCALHOST, CLIENT_PORT))
    self.threadSafePrint("LB: Listening for clients on " + str(LOCALHOST) + ":" + str(CLIENT_PORT))

  def threadSafePrint(self, msg):
    print(msg, flush=True)
    #printLock.acquire()
    #print(msg)
    #printLock.release()

  def run(self):
    global currentClients
    global currentClientsMutex

    self.reqSocket.listen(1)

    while (True):
      if (currentClients < ALLOWED_CLIENTS):
        self.clientSock, self.clientAddr = self.reqSocket.accept()
        self.threadSafePrint("LB: Connected to: " + str(self.clientAddr[0]) + ":" + str(self.clientAddr[1]))
        #thread = threading.Thread(target=self.handleClient, args=(self.clientSock, currentClientsCallback))
        clientThread = ClientThread(self.clientSock, currentClientsCallback)
        currentClientsMutex.acquire()
        try:
          currentClients += 1
          self.threadSafePrint("LB[inc] Number of clients connected to LB: "+str(currentClients))
        finally:
          currentClientsMutex.release()
        #thread.start()
        clientThread.start()


def main():
  # Main thread keeps a socket open and appends to the list
  print("LB: Waiting for connections...", flush=True)

  queueThread = QueueThread()   # Monitors queue
  queueThread.start()

  # Spawn a LoadThread to connect to running load balanced servers
  loadThread = MasterLoadThread()
  loadThread.start()

  clientThread = MasterClientThread()
  clientThread.start()


if __name__ == "__main__":
    main()

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
  #c = Client(100, '', None)
  success = False
  for client in queue:
    if (client.priority < lowest):
      lowest = client.priority
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
            #print("LOWEST PRIORITY")
            #print(client)
            #print("LOWEST LOAD")
            #print(lbServer)
            client.thread.redirAddr = lbServer.ip
            client.thread.redir = True
            queue.remove(client)
        finally:
          queueMutex.release()
      time.sleep(0.2)


# Spawn thread that monitors the load of an individual server

class LoadThread(threading.Thread):
  def __init__(self):
    threading.Thread.__init__(self)
    self.reqSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.reqSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    self.reqSocket.bind((LOCALHOST, LB_PORT))
    self.threadSafePrint("LB: Listening for servers on " + str(LOCALHOST) + ":" + str(LB_PORT))
    self.load = 0

  def threadSafePrint(self, msg):
    printLock.acquire()
    print(msg)
    printLock.release()

  def pingServer(self, server): # Threaded function to check server loads
    while (True):
      print("Going to ask for load values", flush=True)
      connectMsg = '{ \
                      "message": "Hey I need your load values" \
                    }'
      server.sendall(bytes(connectMsg, 'UTF-8'))
      print("Waiting for response", flush=True)
      dataRecv = server.recv(1024).decode()

      dataRecvJson = json.loads(dataRecv)
      if (self.load != dataRecvJson['load']):
        print("Received: %s" % (dataRecvJson), flush=True)

      self.load = dataRecvJson['load']

      time.sleep(0.2)

    server.close()

  def run(self):
    self.reqSocket.listen(1)

    while (True):
      self.serverSock, self.serverAddr = self.reqSocket.accept()
      self.threadSafePrint("LB: Connected to server:" + str(self.serverAddr[0]) + ":" + str(self.serverAddr[1]))
      thread = threading.Thread(target=self.pingServer, args=(self.serverSock,))
      thread.start()        


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
  def __init__(self):
    threading.Thread.__init__(self)
    self.reqSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.reqSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    self.reqSocket.bind((LOCALHOST, CLIENT_PORT))
    self.threadSafePrint("LB: Listening for clients on " + str(LOCALHOST) + ":" + str(CLIENT_PORT))

  def threadSafePrint(self, msg):
    printLock.acquire()
    print(msg)
    printLock.release()
  
  def handleClient(self, client):   # Threaded function to handle single client
    while (True):
      data = client.recv(1024)
      if not data:
        self.threadSafePrint('LB: Closing connection to client')
        break
      sendMutex.acquire()
      redirMessage = '{ \
                        "status": 200, \
                        "ip": "127.0.0.1", \
                        "port": 4001 \
                      }'
      client.send(bytes(redirMessage, 'utf-8'))
      sendMutex.release()
    client.close()

  def run(self):
    self.reqSocket.listen(1)
    baseThreadCount = threading.active_count()
    allowedThreadCount = baseThreadCount + ALLOWED_CLIENTS

    while (True):
        if (threading.active_count() < allowedThreadCount):
            self.clientSock, self.clientAddr = self.reqSocket.accept()
            self.threadSafePrint("LB: Connected to :" + str(self.clientAddr[0]) + ":" + str(self.clientAddr[1]))
            thread = threading.Thread(target=self.handleClient, args=(self.clientSock,))
            thread.start()
        clients = threading.active_count() - baseThreadCount
        self.threadSafePrint("LB: Number of clients connected to LB: "+str(clients))

def main():
  # Main thread keeps a socket open and appends to the list
  print("LB: Waiting for connections...", flush=True)
  
  queueThread = QueueThread()   # Monitors queue
  queueThread.start()
  
  # Spawn a LoadThread to connect to running load balanced servers
  loadThread = LoadThread()  
  loadThread.start()
  loadThreads.append(loadThread)
  
  clientThread = ClientThread()
  clientThread.start()
  

if __name__ == "__main__":
    main()

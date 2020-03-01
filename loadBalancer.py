import socket
#from threading import Thread, Lock
from _thread import *
import threading
import json
#from dataclasses import dataclass
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
  l = LB_Server('127.0.0.1', 4000, 100)
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
  def __init__(self, address, commPort):
    threading.Thread.__init__(self)
    self.address = address
    self.commPort = commPort
    self.load = 0

  def run(self):
    # Constantly ping the associated server for information on the load
    self.commSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.commSock.connect((self.address, self.commPort))
    while (True):
      print("Going to ask for load values", flush=True)
      connectMsg = '{ \
                      "message": "Hey I need your load values" \
                    }'
      self.commSock.sendall(bytes(connectMsg, 'UTF-8'))
      print("Waiting for response", flush=True)
      dataRecv = self.commSock.recv(1024).decode()

      dataRecvJson = json.loads(dataRecv)
      if (self.load != dataRecvJson['load']):
        print("Received: %s" % (dataRecvJson), flush=True)

      self.load = dataRecvJson['load']

      time.sleep(0.2)

    self.commSock.close()


def strToClient(message, thread):
  messageJson = json.loads(message)
  print("message json", flush=True)
  print(messageJson, flush=True)
  return Client(messageJson["priority"], messageJson["message"], thread)

def printClient(m):
  print("(%d) %s;" % (m.priority, m.message), end='', flush=True)
  print(" Thread: ", end='', flush=True)
  print(m.thread, flush=True)

# Thread for each connection
#class ClientThread(Thread):
#  def __init__(self, clientAddr, clientSock, port):
#    Thread.__init__(self)
#    self.redir = False
#    self.redirAddr = ""
#    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#    self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#    LOCALHOST=""
#    self.sock.bind((LOCALHOST, port))
#    print("Server started on %s:%d" % (LOCALHOST, port), flush=True)
#
#  def run(self):
#    print("Waiting for a connection on clientthread", flush=True)
#    print("Waiting for a connection on clientthread")
#    self.sock.listen(1)
#    self.clientSock, self.clientAddr = self.sock.accept()
#    print("New connection added: ", self.clientAddr, flush=True)
#
#    #dataRecv = self.clientSock.recv(2048)
#    #dataDecode = dataRecv.decode()
#    #print("Received: %s" % (dataDecode))
#
#    #dataJson = json.loads(dataDecode)
#    #print(dataJson)
#
#    #if (dataJson["message"] == 'exit' or dataJson["message"] == 'quit'):
#    #  print("Client disconnected")
#    #  return
#
#    while (True):
#      if (self.redir):
#        redirMessage = '{ \
#                          "status": 200, \
#                          "redirect": "' + self.redirAddr + '" \
#                        }'
#        self.clientSock.send(bytes(redirMessage, 'UTF-8'))
#        break;
#      time.sleep(0.5)
#    return

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
      
# Main thread keeps a socket open and appends to the list
#LOCALHOST = "127.0.0.1"
LOCALHOST = ""
PORT = 4000
print("before", flush=True)
reqSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
reqSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
reqSocket.bind((LOCALHOST, PORT))
print("LB: Listening for servers on %s:%d" % (LOCALHOST, PORT), flush=True)
print("LB: Waiting for connections...", flush=True)

listThread = ListThread()   # Monitors queue
listThread.start()

# Spawn a LoadThread for each connected loadBalancedServer.py
loadThread = LoadThread('127.0.0.1', 4000)  
loadThread.start()
loadThreads.append(loadThread)

clientThread = ClientThread()
clientThread.start()

#origPort = 8081 
#
#while (True):
#  reqSocket.listen(1)
#  clientSock, clientAddr = reqSocket.accept()
#
#  dataDecode = clientSock.recv(2048).decode()
#  newThread = ClientThread(clientAddr, clientSock, origPort)
#  client = strToClient(dataDecode, newThread)
#  printClient(client)
#  successMessage = '{ \
#                      "status": 200, \
#                      "port": ' + str(origPort) + ' \
#                    }'
#  origPort = origPort + 1
#  clientSock.send(bytes(successMessage, 'UTF-8'))
#  print("Adding client to queue")
#  queueMutex.acquire()
#  try:
#    queue.append(client)
#    print("Queue now")
#    print(queue)
#  finally:
#    queueMutex.release()
#
#  newThread.start()

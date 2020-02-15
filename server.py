import socket
from threading import Thread, Lock
import json
from dataclasses import dataclass
import time

# Mutex to control access to the list
mutex = Lock()

# Queue
queue = []

def determineLowestPriority():
  lowest = 100
  c = Client('100', '', Thread)
  success = False
  for client in queue:
    if (client.priority < lowest):
      lowest = client.priority
      c = client
      success = True
  return (c, success)

# Spawn thread that monitors the list
class ListThread(Thread):
  def run(self):
    while (True):
      if (True): # if I have open hosts
        mutex.acquire()
        try:
          (client, success) = determineLowestPriority()
          if (success):
            print("LOWEST PRIORITY")
            print(client)
            client.thread.redirAddr = "www.google.com"
            client.thread.redir = True
            queue.remove(client)
        finally:
          mutex.release()
      time.sleep(0.2)


@dataclass
class Client:
  priority: int
  message: str
  thread: Thread

def strToClient(message, thread):
  messageJson = json.loads(message)
  print("message json")
  print(messageJson)
  return Client(messageJson["priority"], messageJson["message"], thread)

def printClient(m):
  print("(%d) %s;" % (m.priority, m.message), end='')
  print(" Thread: ", end='')
  print(m.thread)

# Thread for each connection
class ClientThread(Thread):
  def __init__(self, clientAddr, clientSock, port):
    Thread.__init__(self)
    self.redir = False
    self.redirAddr = ""
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    self.sock.bind((LOCALHOST, port))
    print("Server started on %s:%d" % (LOCALHOST, port))

  def run(self):
    print("Waiting for a connection on clientthread")
    self.sock.listen(1)
    self.clientSock, self.clientAddr = self.sock.accept()
    print("New connection added: ", self.clientAddr)

    #dataRecv = self.clientSock.recv(2048)
    #dataDecode = dataRecv.decode()
    #print("Received: %s" % (dataDecode))

    #dataJson = json.loads(dataDecode)
    #print(dataJson)

    #if (dataJson["message"] == 'exit' or dataJson["message"] == 'quit'):
    #  print("Client disconnected")
    #  return

    while (True):
      if (self.redir):
        redirMessage = '{ \
                          "status": 200, \
                          "redirect": "' + self.redirAddr + '" \
                        }'
        self.clientSock.send(bytes(redirMessage, 'UTF-8'))
        break;
      time.sleep(0.5)
    return


# Main thread keeps a socket open and appends to the list
LOCALHOST = "127.0.0.1"
PORT = 8080
reqSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
reqSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
reqSocket.bind((LOCALHOST, PORT))
print("Server started on %s:%d" % (LOCALHOST, PORT))
print("Waiting for connections...")

listThread = ListThread()
listThread.start()

origPort = 8081

while (True):
  reqSocket.listen(1)
  clientSock, clientAddr = reqSocket.accept()

  dataDecode = clientSock.recv(2048).decode()
  newThread = ClientThread(clientAddr, clientSock, origPort)
  client = strToClient(dataDecode, newThread)
  printClient(client)
  successMessage = '{ \
                      "status": 200, \
                      "port": ' + str(origPort) + ' \
                    }'
  origPort = origPort + 1
  clientSock.send(bytes(successMessage, 'UTF-8'))
  print("Adding client to queue")
  mutex.acquire()
  try:
    queue.append(client)
    print("Queue now")
    print(queue)
  finally:
    mutex.release()

  newThread.start()

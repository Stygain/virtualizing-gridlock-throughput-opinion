import socket
from _thread import *
#from threading import Thread, Lock
import threading
import json
import time

# Main thread keeps a socket open and appends to the list
LOCALHOST = "127.0.0.1"
LB_PORT = 4000
CLIENT_PORT = 4001

mutex = threading.Lock()

clients = 0

class LoadBalancerCommThread(threading.Thread):
  def __init__(self):
    threading.Thread.__init__(self)
    self.reqSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.reqSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    self.reqSocket.bind((LOCALHOST, LB_PORT))
    print("Server started on %s:%d" % (LOCALHOST, LB_PORT))

  def run(self):
    global clients
    print("Waiting for a connection from the Load Balancing Server")
    self.reqSocket.listen(1)
    self.clientSock, self.clientAddr = self.reqSocket.accept()
    print("New connection added to load balancer: ", self.clientAddr)
    while (True):
      dataDecode = self.clientSock.recv(2048).decode()
      #print("Received: " + dataDecode)

      # Check that the message is a request for load?
      mutex.acquire()
      try:
        # send back information about the number of clients currently being serviced
        loadMsg = '{ \
                     "load": ' + str(clients) + ' \
                   }'
        self.clientSock.send(bytes(loadMsg, 'UTF-8'))
        # Temp for demonstration
        clients = clients + 1
      finally:
        mutex.release()

class ClientCommThread(threading.Thread):
  def __init__(self):
    threading.Thread.__init__(self)
    self.reqSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.reqSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    self.reqSocket.bind((LOCALHOST, CLIENT_PORT))
    print("Server started on %s:%d" % (LOCALHOST, CLIENT_PORT))

  def threadSafePrint(self, msg):
    mutex.acquire()
    print(msg)
    mutex.release()

  def handleClient(self, client): # Threaded function
    while (True):
      data = client.recv(1024)
      if not data:
        self.threadSafePrint('Closing connection to client')
        break
      mutex.acquire()
      client.send(data) # Echo data back to client
      mutex.release()
    client.close()

  def run(self):
    self.reqSocket.listen(1)

    allowedThreadCount = threading.active_count() + 5
    while (True):
      if (threading.active_count() < allowedThreadCount):    # Allow up to 5 running threads at a time
        self.clientSock, self.clientAddr = self.reqSocket.accept()
        self.threadSafePrint('Connected to :' + str(self.clientAddr[0]) + ':' + str(self.clientAddr[1]))
        thread = threading.Thread(target=self.handleClient, args=(self.clientSock,))
        thread.start()
        self.threadSafePrint("Number of threads running is now: "+str(threading.active_count()))

lbComm = LoadBalancerCommThread()
lbComm.start()

cComm = ClientCommThread()
cComm.start()


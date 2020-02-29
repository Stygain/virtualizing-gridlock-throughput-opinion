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
ALLOWED_CLIENTS = 5

mutex = threading.Lock()

clients = 0

class LoadBalancerCommThread(threading.Thread):
  def __init__(self):
    threading.Thread.__init__(self)
    self.reqSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.reqSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    self.reqSocket.bind((LOCALHOST, LB_PORT))
    self.threadSafePrint("Server started on " + str(LOCALHOST) + ":" + str(LB_PORT))

  def threadSafePrint(self, msg):
    mutex.acquire()
    print(msg)
    mutex.release()

  def run(self):
    global clients
    self.threadSafePrint("Waiting for a connection from the Load Balancing Server")
    self.reqSocket.listen(1)
    self.clientSock, self.clientAddr = self.reqSocket.accept()
    self.threadSafePrint("New connection added to load balancer: " + str(self.clientAddr))
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
      finally:
        mutex.release()

class ClientCommThread(threading.Thread):
  def __init__(self):
    threading.Thread.__init__(self)
    self.reqSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.reqSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    self.reqSocket.bind((LOCALHOST, CLIENT_PORT))
    self.threadSafePrint("Server started on " + str(LOCALHOST) + ":" + str(CLIENT_PORT))

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
    global clients
    
    self.reqSocket.listen(1)
    baseThreadCount = threading.active_count()
    allowedThreadCount = baseThreadCount + ALLOWED_CLIENTS
    
    while (True):
      clients = threading.active_count() - baseThreadCount    # Update client count
      if (threading.active_count() < allowedThreadCount):   # Only allow up to the number of ALLOWED_CLIENTS
        self.clientSock, self.clientAddr = self.reqSocket.accept()
        self.threadSafePrint('Connected to :' + str(self.clientAddr[0]) + ':' + str(self.clientAddr[1]))
        thread = threading.Thread(target=self.handleClient, args=(self.clientSock,))
        thread.start()
        self.threadSafePrint("Number of threads running is now: "+str(threading.active_count()))

lbComm = LoadBalancerCommThread()
lbComm.start()

cComm = ClientCommThread()
cComm.start()


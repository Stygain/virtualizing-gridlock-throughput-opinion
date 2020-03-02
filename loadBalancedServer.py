import socket
import os
import argparse
from _thread import *
import threading
import json
import time

# Main thread keeps a socket open and appends to the list
LOCALHOST = ""
LB_PORT = 4000
CLIENT_PORT = 4001
ALLOWED_CLIENTS = 5
PID = os.getpid()

mutex = threading.Lock()
clientSendMutex = threading.Lock()

clients = 0

class LoadBalancerCommThread(threading.Thread):
  def __init__(self):
    threading.Thread.__init__(self)
    self.reqSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #self.reqSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    #self.reqSocket.bind((LOCALHOST, LB_PORT))
    self.reqSocket.connect((LOCALHOST, LB_PORT))
    self.threadSafePrint("S: LB comm started on " + str(LOCALHOST) + ":" + str(LB_PORT))

  def threadSafePrint(self, msg):
    print(msg, flush=True)
    #mutex.acquire()
    #try:
    #  print(msg, flush=True)
    #finally:
    #  mutex.release()

  def run(self):
    global clients
    #self.threadSafePrint("S: Waiting for a connection from the Load Balancing Server")
    #self.reqSocket.listen(1)
    #self.clientSock, self.clientAddr = self.reqSocket.accept()
    #self.threadSafePrint("S: New connection added to load balancer: " + str(self.clientAddr))
    while (True):
      dataDecode = self.reqSocket.recv(2048).decode()
#      self.threadSafePrint("S "+ str(PID) +": Received: " + str(dataDecode))
      #print("Received: " + dataDecode)

      # Check that the message is a request for load?
      #self.threadSafePrint("Received: " + str(dataDecode))
      #mutex.acquire()
      #try:
      #  # send back information about the number of clients currently being serviced
      #  loadMsg = '{ \
      #               "load": ' + str(clients) + ' \
      #             }'
      #  self.clientSock.send(bytes(loadMsg, 'UTF-8'))
      #  self.threadSafePrint("Sent: " + str(loadMsg))
      #finally:
      #  mutex.release()

      # send back information about the number of clients currently being serviced
      loadMsg = '{ \
                   "load": ' + str(clients) + ' \
                 }'
      self.reqSocket.send(bytes(loadMsg, 'UTF-8'))
 #     self.threadSafePrint("S: Sent: " + str(loadMsg))

class ClientCommThread(threading.Thread):
  def __init__(self):
    threading.Thread.__init__(self)
    self.reqSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.reqSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    self.reqSocket.bind((LOCALHOST, CLIENT_PORT))
    self.threadSafePrint("S: Listening for clients on " + str(LOCALHOST) + ":" + str(CLIENT_PORT))

  def threadSafePrint(self, msg):
    print(msg, flush=True)
    #mutex.acquire()
    #try:
    #  print(msg, flush=True)
    #finally:
    #  mutex.release()

  def handleClient(self, client): # Threaded function
    while (True):
      data = client.recv(1024)
      if not data:
        self.threadSafePrint('S: Closing connection to client')
        break
      clientSendMutex.acquire()
      try:
        client.send(data) # Echo data back to client
      finally:
        clientSendMutex.release()
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
        self.threadSafePrint('S: Connected to client on :' + str(self.clientAddr[0]) + ':' + str(self.clientAddr[1]))
        thread = threading.Thread(target=self.handleClient, args=(self.clientSock,))
        thread.start()
        self.threadSafePrint("S: Number of client threads running is now: "+str(threading.active_count()))

def main(args):
  global CLIENT_PORT
  CLIENT_PORT = args.cport
 # LB_PORT = args.lbport
  lbComm = LoadBalancerCommThread()
  lbComm.start()

  cComm = ClientCommThread()
  cComm.start()

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  #parser.add_argument('-lbport', type=int, help='Port to connect to load balancer on')
  parser.add_argument('-cport', type=int, help='Port to listen for clients on')
  args = parser.parse_args()
  main(args)

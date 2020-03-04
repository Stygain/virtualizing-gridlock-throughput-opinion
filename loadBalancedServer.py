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
#ALLOWED_CLIENTS = 5
PID = os.getpid()

mutex = threading.Lock()
clientSendMutex = threading.Lock()

currentLoad = 0
currentLoadMutex = threading.Lock()

def currentLoadCallback():
  global currentLoad
  global currentLoadMutex
  currentLoadMutex.acquire()
  try:
    currentLoad -= 1
    print("S[dec] Number of client threads running is now: %d" % currentLoad)
  finally:
    currentLoadMutex.release()

class LoadBalancerCommThread(threading.Thread):
  def __init__(self, clientCommPort, ip):
    threading.Thread.__init__(self)
    self.reqSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #self.reqSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    #self.reqSocket.bind((LOCALHOST, LB_PORT))
    self.reqSocket.connect((LOCALHOST, LB_PORT))
    self.threadSafePrint("S: LB comm started on " + str(LOCALHOST) + ":" + str(LB_PORT))
    self.clientCommPort = clientCommPort
    self.ip = ip

  def threadSafePrint(self, msg):
    print(msg, flush=True)
    #mutex.acquire()
    #try:
    #  print(msg, flush=True)
    #finally:
    #  mutex.release()

  def run(self):
    global currentLoad
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
      # TODO get the real IP
      loadMsg = '{ \
                   "load": ' + str(currentLoad) + ', \
                   "port": ' + str(self.clientCommPort) + ', \
                   "ip": "' + self.ip + '" \
                 }'
      self.reqSocket.send(bytes(loadMsg, 'UTF-8'))
 #     self.threadSafePrint("S: Sent: " + str(loadMsg))

class ClientCommThread(threading.Thread):
  def __init__(self, maxClients):
    threading.Thread.__init__(self)
    self.reqSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.reqSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    self.reqSocket.bind((LOCALHOST, CLIENT_PORT))
    self.threadSafePrint("S: Listening for clients on " + str(LOCALHOST) + ":" + str(CLIENT_PORT))
    self.allowedClients = maxClients

  def threadSafePrint(self, msg):
    print(msg, flush=True)
    #mutex.acquire()
    #try:
    #  print(msg, flush=True)
    #finally:
    #  mutex.release()

  def handleClient(self, client, callback=lambda: None): # Threaded function
    while (True):
      data = client.recv(1024)
      if not data:
        self.threadSafePrint('S: Closing connection to client')
        break
      clientSendMutex.acquire()
      try:
        time.sleep(1) # TODO use random value here
        client.send(data) # Echo data back to client
      finally:
        clientSendMutex.release()
    client.close()
    callback()

  def run(self):
    global currentLoad
    global currentLoadMutex

    self.reqSocket.listen(1)

    while (True):
      if (currentLoad < self.allowedClients):   # Only allow up to the number of ALLOWED_CLIENTS
        self.clientSock, self.clientAddr = self.reqSocket.accept()
        self.threadSafePrint('S: Connected to client on :' + str(self.clientAddr[0]) + ':' + str(self.clientAddr[1]))
        thread = threading.Thread(target=self.handleClient, args=(self.clientSock, currentLoadCallback,))
        currentLoadMutex.acquire()
        try:
          currentLoad += 1
          self.threadSafePrint("S[inc] Number of client threads running is now: "+str(currentLoad))
        finally:
          currentLoadMutex.release()
        thread.start()

def main(args):
  global CLIENT_PORT
  CLIENT_PORT = args.cport
 # LB_PORT = args.lbport
  lbComm = LoadBalancerCommThread(CLIENT_PORT, args.ip)
  lbComm.start()

  cComm = ClientCommThread(args.ccount)
  cComm.start()

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  #parser.add_argument('-lbport', type=int, help='Port to connect to load balancer on')
  parser.add_argument('-cport', type=int, required=True, help='Port to listen for clients on')
  parser.add_argument('-ccount', type=int, required=True, help='Max number of clients this server can handle')
  parser.add_argument('-ip', type=str, required=True, help='IP address of server')
  args = parser.parse_args()
  main(args)

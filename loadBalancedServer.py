import socket
from threading import Thread, Lock
import json
import time

# Main thread keeps a socket open and appends to the list
LOCALHOST = "127.0.0.1"
LB_PORT = 4000

mutex = Lock()

clients = 0

class LoadBalancerCommThread(Thread):
  def __init__(self):
    Thread.__init__(self)
    self.reqSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.reqSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    self.reqSocket.bind((LOCALHOST, LB_PORT))
    print("Server started on %s:%d" % (LOCALHOST, LB_PORT))

  def run(self):
    global clients
    print("Waiting for a connection from the Load Balancing Server")
    while (True):
      self.reqSocket.listen(1)
      self.clientSock, self.clientAddr = self.reqSocket.accept()
      print("New connection added to load balancer: ", self.clientAddr)

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


lbComm = LoadBalancerCommThread()
lbComm.start()

# TODO Add in implementation for actual server assets


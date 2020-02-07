import socket
import threading

LOCALHOST = "127.0.0.1"
PORT = 8080
reqSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
reqSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
reqSocket.bind((LOCALHOST, PORT))
print("Server started on %s:%d" % (LOCALHOST, PORT))
print("Waiting for connections...")

while (True):
  reqSocket.listen(1)
  clientSock, clientAddr = reqSocket.accept()
  while (True):
    dataRecv = clientSock.recv(2048)
    dataDecode = dataRecv.decode()
    print("Received: %s" % (dataDecode))
    if (dataDecode == 'exit' or dataDecode == 'quit'):
      break
    clientSock.send(bytes(dataDecode, 'UTF-8'))
  print("Client disconnected")

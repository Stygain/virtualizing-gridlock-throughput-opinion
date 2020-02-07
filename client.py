import socket

LOCALHOST = "127.0.0.1"
PORT = 8080
clientSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientSock.connect((LOCALHOST, PORT))
clientSock.sendall(bytes("This is a message", 'UTF-8'))
while (True):
  dataRecv = clientSock.recv(1024)
  print("Received: %s" % (dataRecv.decode()))
  inp = input()
  clientSock.sendall(bytes(inp, 'UTF-8'))
  if (inp == 'exit' or inp == 'quit'):
    break

clientSock.close()

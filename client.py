import socket
import json

LOCALHOST = "127.0.0.1"
PORT = 8080
clientSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientSock.connect((LOCALHOST, PORT))

msg = '{ \
        "priority": 2, \
        "message": "This is my message" \
      }'

#msgJson = json.loads(msg)
#print(msgJson)

clientSock.sendall(bytes(msg, 'UTF-8'))
while (True):
  dataRecv = clientSock.recv(1024)
  print("Received: %s" % (dataRecv.decode()))
  inp = input()
  newMsg = '{ \
              "priority": 1, \
              "message": "' + inp + '" \
            }'
  clientSock.sendall(bytes(newMsg, 'UTF-8'))
  if (inp == 'exit' or inp == 'quit'):
    break

clientSock.close()

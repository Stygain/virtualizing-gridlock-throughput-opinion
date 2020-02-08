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
thanks = '{ \
            "priority": 2, \
            "message": "Thanks" \
          }'

clientSock.sendall(bytes(msg, 'UTF-8'))
dataRecv = clientSock.recv(1024)
print("Received: %s" % (dataRecv.decode()))
clientSock.sendall(bytes(thanks, 'UTF-8'))

# Receive the redirect
dataRecv = clientSock.recv(1024)
print("Received: %s" % (dataRecv.decode()))

clientSock.close()

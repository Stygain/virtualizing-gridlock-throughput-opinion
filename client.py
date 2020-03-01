import socket
import time
import json

LOCALHOST = "127.0.0.1"
PORT = 8081
clientSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientSock.connect((LOCALHOST, PORT))

connectMsg = '{ \
                "priority": 2, \
                "message": "Request to connect" \
              }'
#msg = '{ \
#        "priority": 2, \
#        "message": "This is my message" \
#      }'
#thanks = '{ \
#            "priority": 2, \
#            "message": "Thanks" \
#          }'

clientSock.sendall(bytes(connectMsg, 'UTF-8'))
dataRecv = clientSock.recv(1024).decode()
print("Received: %s" % (dataRecv))

dataRecvJson = json.loads(dataRecv)
print(dataRecvJson)
print("Port: %d" % (dataRecvJson["port"]))
print("Server IP: %s" % (dataRecvJson["ip"]))


# Disconnect, connect to new port
clientSock.close()

#time.sleep(0.1)
#secondSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#secondSock.connect((LOCALHOST, int(dataRecvJson["port"])))
#clientSock.sendall(bytes(thanks, 'UTF-8'))

# Receive the redirect
#dataRecv = secondSock.recv(1024)
#print("Received: %s" % (dataRecv.decode()))

#secondSock.close()

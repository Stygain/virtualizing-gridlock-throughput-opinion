import socket
import time
import json

LOCALHOST = "127.0.0.1"
PORT = 8081

while (True):
    clientSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientSock.connect((LOCALHOST, PORT))

    connectMsg = '{ \
                    "priority": 2, \
                    "message": "Request to connect" \
                  }'
    msg = '{ \
            "priority": 2, \
            "message": "This is my message" \
           }'

    clientSock.sendall(bytes(connectMsg, 'UTF-8'))
    dataRecv = clientSock.recv(1024).decode()
    #print("C: Received: %s" % (dataRecv))

    dataRecvJson = json.loads(dataRecv)
    print("C: Received: %s" % (dataRecvJson))
    print("C: Redirect port: %d" % (dataRecvJson["port"]))
    print("C: Redirect server IP: %s" % (dataRecvJson["ip"]))


    # Disconnect, connect to new port
    clientSock.close()

    time.sleep(0.1)
    serverSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSock.connect((dataRecvJson['ip'], int(dataRecvJson['port'])))
    serverSock.sendall(bytes(msg, 'UTF-8'))

    dataRecv = serverSock.recv(1024)
    print("C: Received from server: %s" % (dataRecv.decode()))
    serverSock.close()

    # Receive the redirect
    #dataRecv = secondSock.recv(1024)
    #print("Received: %s" % (dataRecv.decode()))

    #secondSock.close()
    time.sleep(2) # TODO add random sleep

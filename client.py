import socket
import time
from datetime import datetime
import json
import os

PID = os.getpid()
LOCALHOST = "127.0.0.1"
PORT = 8081

packetsSent = 0
priority = 2

RTTFilename = "RTTClient"+str(PID)


while (True):
    
    startTime = datetime.now()  # Get time in milliseconds

    clientSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientSock.connect((LOCALHOST, PORT))

    connectMsg = '{ \
                    "priority": '+str(priority)+', \
                    "message": "Request to connect" \
                  }'
    msg = '{ \
            "priority": '+str(priority)+', \
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

    endTime = datetime.now()  # Get end time
    dt = endTime - startTime
    roundTripTime = (dt.days * 24 * 60 * 60 + dt.seconds) * 1000 + dt.microseconds / 1000.0
    f=open(RTTFilename, "a+")
    f.write(str(priority)+","+str(roundTripTime)+"\n")
    f.close()

    packetsSent += 1
    print("C: Packets successfully transmitted: %d" % (packetsSent))

    # Receive the redirect
    #dataRecv = secondSock.recv(1024)
    #print("Received: %s" % (dataRecv.decode()))

    #secondSock.close()
    time.sleep(2) # TODO add random sleep

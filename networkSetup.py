import subprocess
import os
import sys
import argparse
import time

parser = argparse.ArgumentParser()
parser.add_argument('-algo', type=str, required=True, help="Algorithm to use")
parser.add_argument('-clientCount', type=int, required=True, help="Number of clients")
parser.add_argument('-serverCount', type=int, required=True, help="Number of servers")

args = parser.parse_args()

if (args.algo != "ROUND_ROBIN" and args.algo != "LEAST_CONNECTIONS"):
    print("Error, algorithm not recognized")
    sys.exit(1)

#subprocess.call("./loadBalancer.py -algo ROUND_ROBIN &")
execString = "python3 loadBalancer.py -algo " + args.algo + " &"
os.system(execString)

port = 4001
ccountArr = [2, 5, 3, 4, 6, 1]
for i in range(args.serverCount):
    thisPort = port + i
    execString = "python3 loadBalancedServer.py -cport " + str(thisPort) + " -ccount " + str(ccountArr[i]) + " -ip '127.0.0.1' &"
    #subprocess.call(execString)
    os.system(execString)

time.sleep(2)

for i in range(args.clientCount):
    execString = "python3 client.py &"
    #subprocess.call(execString)
    os.system(execString)
    time.sleep(0.2)

time.sleep(120)     # Run for 2 minutes
killString = "killall python3"
os.system(killString)


#!/usr/bin/python3

import csv
#from os import listdir
#from os.path import isfile, join
import glob

files = glob.glob('./RTT*')
#files = glob.glob('./RTTClient12807')

print("Files")
print(files)

rtt = []
rtt.append([])
rtt.append([])
rtt.append([])
rtt.append([])
rtt.append([])
rtt.append([])
rtt.append([])
rtt.append([])
rtt.append([])
rtt.append([])

for f in files:
    print('file: ' + f)
    with open(f) as csvFile:
        csvReader = csv.reader(csvFile, delimiter=',')
        for row in csvReader:
            #print("APPENDING: " + row[1] + " to index " + str(int(row[0]) - 1))
            (rtt[int(row[0])-1]).append(row[1])

runningAverageArr = []
runningAverageArr.append([])
runningAverageArr.append([])
runningAverageArr.append([])
runningAverageArr.append([])
runningAverageArr.append([])
runningAverageArr.append([])
runningAverageArr.append([])
runningAverageArr.append([])
runningAverageArr.append([])
runningAverageArr.append([])


index = 0
for priority in rtt:
    print(priority)
    count = 0
    runningTotal = 0
    for rttVal in priority:
        runningTotal += float(rttVal)
        runningAverageArr[index].append(str(runningTotal / (count + 1)))
        count += 1

    index += 1


writeFile = open('data.csv', 'w')
index = 0
for priority in runningAverageArr:
    index += 1
    writeFile.write("Priority " + str(index) + ",")
    writeFile.write(",".join(priority))
    writeFile.write("\n")
writeFile.close()

import socket
from matplotlib import pyplot as plt
import hashlib
import threading
import os
import sys
import timeit
from queue import PriorityQueue

host1 = 'vayu.iitd.ac.in'
host2 = 'norvig.com'
file = 'big.txt'
port = 80
numTCP = (int)(sys.argv[2])
output_file = 'Q3Mult.txt'
chunkSize = (int)(sys.argv[1])
start = 0
data = PriorityQueue()
start_time = timeit.default_timer()

fb = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
fb.connect((host1, port))
fbrequest = 'GET /big.txt HTTP/1.1\r\nHost:%s\r\nConnection: keep-alive\r\nRange: bytes=%s\r\n\r\n' % (host1, '0-1')
fb.send(fbrequest.encode())

header = ''
while True:
    msg = fb.recv(1)
    header += msg.decode()
    if '\r\n\r\n' in header:
        break

l = header.find("Content-Range")
fileSize = (int)(header[l:].split('\r\n')[0].split("/")[1])

print("Hostname: {}, {}".format(host1, host2))
print("Accessing File: {}".format(file))
print("chunkSize = {}".format(chunkSize))
print("Number of Parallel TCP connections on each server = {}".format(numTCP))
print("Downloading in File: {}".format(output_file))
print()


def getRequest():
    global start
    a = start
    b = start + chunkSize
    if b > fileSize:
        b = fileSize
        start = fileSize
        return a, b
    start += chunkSize + 1
    return a, b

def sendRequest(host, threadName):
    global start
    global data
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    while start != fileSize:
        a, b = getRequest()
        part = str(a) + '-' + str(b)
        request = 'GET /%s HTTP/1.1\r\nHost:%s\r\nConnection: keep-alive\r\nRange: bytes=%s\r\n\r\n' % (file, host, part)
        print(threadName, part)
        s.send(request.encode())
        header = ''
        d = ''
        while True:
            msg = s.recv(1)
            if len(msg) < 1:
                s.close()
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((host, port))
                s.send(request.encode())
                continue
            header += str(msg)[2:-1]
            if '\\r\\n\\r\\n' in header:
                break

        for i in range(chunkSize+1):
            msg = s.recv(1)
            d += msg.decode()
        data.put((a, d))
    s.close()

threads = []

for i in range(numTCP):
    t1 = threading.Thread(target=sendRequest, args=(host1, "VayuThread-" + str(i),))
    t2 = threading.Thread(target=sendRequest, args=(host2, "NorvigThread-" + str(i),))
    t1.start()
    t2.start()
    threads.append(t1)
    threads.append(t2)

for t in threads:
    t.join()

end_time = timeit.default_timer()
time_taken = (end_time - start_time)

f = open(output_file, 'w')
MD5Sum = hashlib.md5()

while not data.empty():
    s = data.get()
    MD5Sum.update(s[1].encode())
    print(s[1], end='', file=f)

f.close()

print('MD5Sum = {}'.format(MD5Sum.hexdigest()))
print('Time to Download = {}'.format(time_taken))
print()
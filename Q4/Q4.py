import socket
from matplotlib import pyplot as plt
import hashlib
import threading
import os
import sys
import timeit
from queue import PriorityQueue

host = sys.argv[1]
file = sys.argv[2]
port = 80
numTCP = (int)(sys.argv[4])
output_file = sys.argv[5] + '.txt'
chunkSize = (int)(sys.argv[3])
start = 0
data = PriorityQueue()
start_time = timeit.default_timer()

fb = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
fb.connect((host, port))
fbrequest = 'GET /big.txt HTTP/1.1\r\nHost:%s\r\nConnection: keep-alive\r\nRange: bytes=%s\r\n\r\n' % (host, '0-1')
fb.send(fbrequest.encode())

header = ''
while True:
    msg = fb.recv(1)
    header += msg.decode()
    if '\r\n\r\n' in header:
        break

l = header.find("Content-Range")
fileSize = (int)(header[l:].split('\r\n')[0].split("/")[1])

print("Hostname: {}".format(host))
print("Accessing File: {}".format(file))
print("chunkSize = {}".format(chunkSize))
print("Number of Parallel TCP connections = {}".format(numTCP))
print("Downloading in File: {}".format(output_file))

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

loglist = []

def sendRequest(l, threadName):
    global start
    global data
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(20)
    s.connect((host, port))
    while start != fileSize:
        a, b = getRequest()
        part = str(a) + '-' + str(b)
        request = 'GET /%s HTTP/1.1\r\nHost:%s\r\nConnection: keep-alive\r\nRange: bytes=%s\r\n\r\n' % (file, host, part)
        print(threadName, part)
        s.send(request.encode())
        header = ''
        d = ''
        flag = 0
        while True:
            if flag == 0:
                try:
                    msg = s.recv(1)
                    if len(msg) < 1:
                        s.close()
                        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        s.settimeout(20)
                        s.connect((host, port))
                        s.send(request.encode())
                        header = ''
                        continue
                    header += str(msg)[2:-1]
                    if '\\r\\n\\r\\n' in header:
                        flag = 1
                except:
                    s.close()
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(20)
                    while True:
                        try:
                            s.connect((host, port))
                            s.send(request.encode())
                            header = ''
                            break
                        except:
                            s.close()
                            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            s.settimeout(20)
            else:
                for i in range(chunkSize+1):
                    try:
                        msg = s.recv(1)
                        d += msg.decode()
                    except:
                        s.close()
                        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        s.settimeout(20)
                        while True:
                            try:
                                s.connect((host, port))
                                s.send(request.encode())
                                break
                            except:
                                s.close()
                                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                                s.settimeout(20)
                        flag = 0
                        header = ''
                        d = ''
                        break

                if flag == 1:
                    break
        data.put((a, d))
        kt2 = timeit.default_timer()
        l.append((b, kt2-start_time))
    s.close()
    loglist.append(l)

threads = []

for i in range(numTCP):
    l = []
    t = threading.Thread(target=sendRequest, args=(l, "Thread-" + str(i),))
    t.start()
    threads.append(t)

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

plt.figure()
for i in range(len(loglist)):
    l1 = loglist[i]
    timek = []
    bytek = []
    lb = 'Connection-' + str(i)
    for j in range(len(l1)):
        timek.append(l1[j][1])
        bytek.append(l1[j][0])
    plt.plot(timek, bytek, label=lb)

plt.legend()
plt.title('TCP Connection Log with Network Disconnections')
plt.ylabel('Bytes Downloaded')
plt.xlabel('Time')
c = 'Log' + sys.argv[5] + '.png'
plt.savefig(c)
plt.show()
plt.close()
import socket
import sys
import timeit

host = sys.argv[1]
part = sys.argv[2]
port = 80

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, port))

request = 'GET /big.txt HTTP/1.1\r\nHost:%s\r\nConnection: keep-alive\r\nRange: bytes=%s\r\n\r\n' % (host, part)
s.send(request.encode())

f = open('Q2.txt', 'w')

header = ''
while True:
	msg = s.recv(1)
	header += msg.decode()
	if '\r\n\r\n' in header:
		break

print(header)

while True:
	msg = s.recv(1)
	if len(msg) < 1:
		break
	if msg.decode() == '\n':
		print(file=f)
	else:
		print(msg.decode(), end='', file=f)

f.close()


import socket
import hashlib
import sys

host = sys.argv[1]
port = 80

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, port))

request = 'GET /big.txt HTTP/1.1\r\nHost:%s\r\n\r\n' % host
s.send(request.encode())

f = open('Q1.txt', 'w')
MD5Sum = hashlib.md5()

header = ''
while True:
	msg = s.recv(1)
	if msg.decode() == '\n':
		print()
	else:
		print(msg.decode(), end='')
	header += msg.decode()
	if '\r\n\r\n' in header:
		break

while True:
	msg = s.recv(1)
	MD5Sum.update(msg)
	if len(msg) < 1:
		break
	if msg.decode() == '\n':
		print(file=f)
	else:
		print(msg.decode(), end='', file=f)

f.close()
print('MD5Sum = {}'.format(MD5Sum.hexdigest()))
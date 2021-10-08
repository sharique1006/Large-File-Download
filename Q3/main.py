import subprocess
import numpy as np

input = np.loadtxt('input.csv', dtype=str)
chunkSize = 102399

def parseURL(url):
	x = url.split(":")[1].split("/")
	host = x[2]
	file = x[3]
	return host, file

i = 0
for inp in input:
	i += 1
	host, file = parseURL(inp[0])
	tcp = inp[1]
	output_file = 'out' + str(i)
	subprocess.run(["python3", "Q3.py", host, file, str(chunkSize), tcp, output_file])
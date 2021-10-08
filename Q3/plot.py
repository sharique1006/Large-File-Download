from matplotlib import pyplot as plt
import timeit
import subprocess

numTCP = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
times = []
chunkSize = 10239

for x in numTCP:
	print('Number of TCP Connections = {}'.format(x))
	start = timeit.default_timer()
	f = "plot" + str(x)
	subprocess.run(["python3", "Q3.py", "vayu.iitd.ac.in", "big.txt", str(chunkSize), str(x), f, "1"])
	end = timeit.default_timer()
	print("Time to Download = ", (end-start))
	print()
	times.append(end-start)

plt.figure()
plt.plot(numTCP, times)
plt.title('Performance Comparison')
plt.xlabel('Number of Parallel TCP Connections')
plt.ylabel('Download Time(s)')
plt.savefig("plot.png")
plt.show()
plt.close()
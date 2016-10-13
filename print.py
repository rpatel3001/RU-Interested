import pickle
import sys

args = sys.argv[1:]

dataFile = open("data.dat", "rb")

data = pickle.load(dataFile)

dataFile.close()

for t in data[args[0]][args[2]]:
	if abs(t["time"] - int(args[1])) < 100:
		print(str(t["time"]) + " " + t["day"] + " " + t["building"] + " " + t["room"] + " " + t["title"] + "\n")
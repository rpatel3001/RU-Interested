import json
import requests
import json

url = "http://sis.rutgers.edu/soc/init.json"
ret = requests.get(url);
data = {"buildings" : ret.json()["buildings"], "subjects" : ret.json()["subjects"]}

dataFile = open("data.dat", "w")

json.dump(data, dataFile, indent=4, separators=(',', ': '))

dataFile.close()
import json
import requests
import pickle

url = "http://sis.rutgers.edu/soc/courses.json"
specs = {"semester" : "92016", "campus" : "NB", "level" : "U", "subject" : "332"}
ret = requests.get(url, params=specs);
busch = {}
livi = []
cookdoug = []
collegeave = []

for i in ret.json():
	for j in i["sections"]:
		if j["campusCode"] == "OB":
			continue
		for k in j["meetingTimes"]:
			if k["meetingModeCode"] == "90" or k["meetingModeCode"] == "19" or k["meetingModeCode"] == "03" or k["startTime"] == None or k["buildingCode"] == None or k["roomNumber"] == None:
				continue
			c = {}
			c["courseNum"] = i["courseNumber"]
			if i["expandedTitle"]:
				c["title"] = i["expandedTitle"].strip()
			else:
				c["title"] = i["title"].strip()
			c["building"] = k["buildingCode"]
			c["room"] = k["roomNumber"]
			#c["source"] = j
			c["day"] = k["meetingDay"]
			temp = int(k["startTime"])
			if temp < 1200 and k["pmCode"] == "P":
				temp += 1200
			c["time"] = temp
			if k["campusLocation"] == "1":
				collegeave.insert(0,c)
			elif k["campusLocation"] == "2":
				if(not c["building"] in busch):
					busch[c["building"]] = []
				busch[c["building"]].insert(0,c)
			elif k["campusLocation"] == "3":
				livi.insert(0,c)
			elif k["campusLocation"] == "4":
				cookdoug.insert(0,c)
			else:
				print(k["campusLocation"] + " " +  k["campusName"] + " " + j["index"])
				assert(False)

data = {"COLLEGE AVENUE" : collegeave, "LIVINGSTON" : livi, "DOUGLAS/COOK" : cookdoug, "BUSCH" : busch}

dataFile = open("data.dat", "wb")

pickle.dump(data, dataFile)

dataFile.close()
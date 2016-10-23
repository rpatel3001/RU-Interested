import json
import requests

dataInFile = open("data.dat", "r")
dataIn = json.load(dataInFile)
dataInFile.close()

url = "http://sis.rutgers.edu/soc/courses.json"
specs = {"semester" : "92016", "campus" : "NB", "level" : "U", "subject" : ""}
busch = []
livi = []
cookdoug = []
collegeave = []

for subj in dataIn["subjects"]:
	print("Processing " + subj["description"])
	specs["subject"] = subj["code"]
	ret = requests.get(url, params=specs);
	for i in ret.json():
		for j in i["sections"]:
			if j["campusCode"] == "OB":
				continue
			for k in j["meetingTimes"]:
				if k["meetingModeCode"] == "90" or k["meetingModeCode"] == "19" or k["meetingModeCode"] == "03" or k["startTime"] == None or k["buildingCode"] == None or k["roomNumber"] == None:
					continue
				c = {}
				c["department"] = subj["description"]
				c["courseNum"] = subj["code"] + ":" + i["courseNumber"]
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
				temp = str(temp)
				c["prettyTime"] = temp[:-2] + ":" + temp[-2:]
				if k["campusLocation"] == "1":
					collegeave.insert(0,c)
				elif k["campusLocation"] == "2":
					busch.insert(0,c)
				elif k["campusLocation"] == "3":
					livi.insert(0,c)
				elif k["campusLocation"] == "4":
					cookdoug.insert(0,c)
				elif k["campusLocation"] == "5":
					pass
				else:
					print(k["campusLocation"] + " " +  k["campusName"] + " " + j["index"])
					assert(False)

busch = sorted(busch, key=lambda k: k['time'])
livi = sorted(livi, key=lambda k: k['time'])
cookdoug = sorted(cookdoug, key=lambda k: k['time'])
collegeave = sorted(collegeave, key=lambda k: k['time'])

data = {1 : collegeave, 3: livi, 4 : cookdoug, 2: busch}

dataFile = open("classes.dat", "w")

json.dump(data, dataFile, indent=4, separators=(',', ': '))

dataFile.close()
import json
import requests
import os
import psycopg2
import urllib.parse as urlparse

#init postgresql table
if os.environ.get('HEROKU'):
	urlparse.uses_netloc.append("postgres")
	url = urlparse.urlparse(os.environ["DATABASE_URL"])
	conn = psycopg2.connect(
	    database=url.path[1:],
	    user=url.username,
	    password=url.password,
	    host=url.hostname,
	    port=url.port
	)
else:
	conn = psycopg2.connect("dbname=DATABASE user=postgres")
cur = conn.cursor()

#scrape building and subject code data
url = "http://sis.rutgers.edu/soc/init.json"
ret = requests.get(url);
initData = {"buildings" : ret.json()["buildings"], "subjects" : ret.json()["subjects"]}

#scrape class listings
url = "http://sis.rutgers.edu/soc/courses.json"
specs = {"semester" : "92016", "campus" : "NB", "level" : "U", "subject" : ""}
busch = []
livi = []
cookdoug = []
collegeave = []

cur.execute("TRUNCATE TABLE buildings;")
for b in initData["buildings"]:
	cur.execute("INSERT INTO buildings VALUES (%s, %s, %s)",(b["code"],b["name"],int(b["id"])))

conn.commit()

cur.execute("TRUNCATE TABLE subjects;")
for subj in initData["subjects"]:
	cur.execute("INSERT INTO subjects VALUES (%s, %s)", (subj["description"], subj["code"]))
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
				c["deptcode"] = subj["code"]
				c["coursecode"] = i["courseNumber"]
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
					c["campus"] = 1
					collegeave.insert(0,c)
				elif k["campusLocation"] == "2":
					c["campus"] = 2
					busch.insert(0,c)
				elif k["campusLocation"] == "3":
					c["campus"] = 3
					livi.insert(0,c)
				elif k["campusLocation"] == "4":
					c["campus"] = 4
					cookdoug.insert(0,c)
				elif k["campusLocation"] == "5":
					pass
				else:
					print(k["campusLocation"] + " " +  k["campusName"] + " " + j["index"])
					assert(False)

conn.commit()

busch = sorted(busch, key=lambda k: k['time'])
livi = sorted(livi, key=lambda k: k['time'])
cookdoug = sorted(cookdoug, key=lambda k: k['time'])
collegeave = sorted(collegeave, key=lambda k: k['time'])
data = {1 : collegeave, 3: livi, 4 : cookdoug, 2: busch}

#add to database
cur.execute("TRUNCATE TABLE classes;")
for d in data:
	for m in data[d]:
		cur.execute("INSERT INTO classes VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", (m["title"], m["room"], m["department"], m["day"], m["time"], m["building"], m["deptcode"], m["coursecode"], m["campus"]))

conn.commit()
cur.close()
conn.close()
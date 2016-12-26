import json
import requests
import os
import psycopg2
import urllib.parse as urlparse
from bs4 import BeautifulSoup
from difflib import SequenceMatcher
from unidecode import unidecode

minimumcapacity = 50

def strdist(s1, s2):
	return SequenceMatcher(None, s1, s2).ratio()
print("connecting to database")

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
	conn = psycopg2.connect("dbname=database user=postgres")
cur = conn.cursor()


print('creating tables')
cur.execute("create table if not exists rooms (building text, campus text, buildingcode text, roomnum text, capacity int)")
cur.execute("create table if not exists departments(name text,code text)")
cur.execute("create table if not exists classes (title text, room text, department text, day text, time integer, building text, deptcode text, coursecode text, campus text)")


print('scraping room information')
ids = requests.get('https://dcs.rutgers.edu/classrooms/building-identification-codes')
ids = BeautifulSoup(ids.text, 'html.parser').table.table.find_all('tr')[1:]
ids = [[y.string.strip() for y in x if y.string.strip() != ''] for x in ids]

rooms = requests.get('https://dcs.rutgers.edu/classrooms/find-a-classroom?items_per_page=All')
rooms = BeautifulSoup(rooms.text, 'html.parser').find(id='tabs-3').find_all('tr', class_=['odd','even'])
rooms = [x.find_all('td') for x in rooms]
for i in range(len(rooms)):
	rooms[i][0] = rooms[i][0].a
	rooms[i] = [unidecode(x.string).strip() for x in rooms[i]]
	j = rooms[i][0].index(' - ')
	rooms[i] = (rooms[i][0][:j], rooms[i][0][j+3:].replace('Room ', '').replace('Auditorium', 'AUD').replace('EDR-204', 'EDR').replace('MPR-205', 'MPR'), rooms[i][1], rooms[i][2])
rooms = [x for x in rooms if x[3] != '' and int(x[3]) > minimumcapacity]

roomcodes=[]
cur.execute('TRUNCATE TABLE rooms')
for i in range(len(rooms)):
	building = max(ids, key=lambda x: strdist(x[1], rooms[i][0]))
	res = (rooms[i][0], building[2].replace('/', ''), building[0], rooms[i][1], rooms[i][3])
	roomcodes.append(res[2] + '-' + res[3])
	cur.execute("INSERT INTO rooms VALUES (%s, %s, %s, %s, %s)", res)
conn.commit()

print('scraping department information')
subjects = requests.get('http://sis.rutgers.edu/soc/init.json').json()["subjects"]

cur.execute("TRUNCATE TABLE departments")
for b in subjects:
	cur.execute("INSERT INTO departments VALUES (%s, %s)",(b["description"],b["code"]))

conn.commit()


print('scraping class information')
url = "http://sis.rutgers.edu/soc/courses.json"
specs = {"semester" : "12017", "campus" : "NB", "level" : "U", "subject" : ""}
busch = []
livi = []
cookdoug = []
collegeave = []

for subj in subjects:
	print("Processing " + subj["description"])
	specs["subject"] = subj["code"]
	ret = requests.get(url, params=specs);
	for i in ret.json():
		for j in i["sections"]:
			if j["campusCode"] == "OB":
				continue
			for k in j["meetingTimes"]:
				if k["meetingModeCode"] == "90" or k["meetingModeCode"] == "19" or k["meetingModeCode"] == "03" \
				  or k["startTime"] == None or k["buildingCode"] == None or k["roomNumber"] == None \
				  or k["buildingCode"] + '-' + k["roomNumber"] not in roomcodes:
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
					c["campus"] = "CAC"
					collegeave.insert(0,c)
				elif k["campusLocation"] == "2":
					c["campus"] = "BUS"
					busch.insert(0,c)
				elif k["campusLocation"] == "3":
					c["campus"] = "LIV"
					livi.insert(0,c)
				elif k["campusLocation"] == "4":
					c["campus"] = "CD"
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

print('adding classes to database')
cur.execute("TRUNCATE TABLE classes")
for d in data:
	for m in data[d]:
		cur.execute("INSERT INTO classes VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", (m["title"], m["room"], m["department"], m["day"], m["time"], m["building"], m["deptcode"], m["coursecode"], m["campus"]))

conn.commit()
cur.close()
conn.close()

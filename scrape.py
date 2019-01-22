import json
import requests
import os
import psycopg2
from json import dumps
import urllib.parse as urlparse
from bs4 import BeautifulSoup
from difflib import SequenceMatcher
from unidecode import unidecode
import re
from pprint import pprint

minimumcapacity = 30

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


print('\ncreating tables')
cur.execute("create table if not exists rooms (building text, campus text, buildingcode text, roomnum text, capacity int)")
cur.execute("create table if not exists departments(name text,code text)")
cur.execute("create table if not exists courses (title text, room text, department text, day text, startTime integer, endTime integer, building text, deptcode text, coursecode text, campus text)")
'''
print('\nscraping room information')
ids = requests.get('https://dcs.rutgers.edu/classrooms/building-identification-codes')
ids = BeautifulSoup(ids.text, 'html.parser').table.table.find_all('tr')[1:]
ids = [[y.string.strip() for y in x if y.string.strip() != ''] for x in ids]

rooms = requests.get('https://dcs.rutgers.edu/classrooms/find-a-classroom?items_per_page=All')
rooms = BeautifulSoup(rooms.text, 'html.parser').find_all('tr', class_=['odd','even'])
rooms = [x.find_all('td') for x in rooms]
for i in range(len(rooms)):
	rooms[i][0] = rooms[i][0].a
	rooms[i] = [unidecode(x.string).strip() for x in rooms[i]]
	j = rooms[i][0].index(' - ')
	rooms[i] = (rooms[i][0][:j], rooms[i][0][j+3:].replace('Room ', '').replace('Auditorium', 'AUD').replace('EDR-204', 'EDR').replace('MPR-205', 'MPR'), rooms[i][1], rooms[i][2])
#	pprint(rooms[i])

roomcodes=[]
print("Truncating rooms")
cur.execute('TRUNCATE TABLE rooms')
print("Inserting rooms")
for i in range(len(rooms)):
#	pprint(rooms[i])
	building = max(ids, key=lambda x: strdist(x[1], rooms[i][0]))
	res = (rooms[i][0], building[2].replace('/', ''), building[0], rooms[i][1], rooms[i][3])
	roomcodes.append(res[2] + '-' + res[3])
	cur.execute("INSERT INTO rooms VALUES (%s, %s, %s, %s, %s)", res)
conn.commit()
'''

print('\nretrieving department information')

subjects = requests.get('http://sis.rutgers.edu/oldsoc/init.json')
try:
	subjects = subjects.json()["subjects"]
	print("Getting new list")
	cur.execute("TRUNCATE TABLE departments")
	for b in subjects:
	       cur.execute("INSERT INTO departments VALUES (%s, %s)",(b["description"],b["code"]))
	conn.commit()
except:
	print("Using old list")
	cur.execute("SELECT * from departments")
	subjects = cur.fetchall()
	subjects = [{"description": x[0], "code": x[1]} for x in subjects]


print('\nscraping class information')
url = "http://sis.rutgers.edu/soc/courses.gz"
specs = {"year" : "2019", "term" : "1", "campus" : "NB"}

buschs = set()
livis = set()
cookdougs = set()
collegeaves = set()

busch = []
livi = []
cookdoug = []
collegeave = []

ret = str(requests.get(url, params=specs).content)[2:-1].replace("\\'", "'").replace("\\\\\"", "'").replace("\\xbf\\xbf", "'")
ret = re.sub("\s+", " ", ret)
ret = json.loads(ret)

for i in ret:
	for j in i["sections"]:
		if j["campusCode"] == "OB":
			continue
		for k in j["meetingTimes"]:
			if k["campusLocation"] == "5" or k["meetingModeCode"] == "90" \
			  or k["meetingModeCode"] == "09" or k["meetingModeCode"] == "05" \
			  or k["meetingModeCode"] == "19" or k["meetingModeCode"] == "03" \
			  or k["startTime"] == None or k["buildingCode"] == None or k["roomNumber"] == None:
				continue
#			if k["buildingCode"] + '-' + k["roomNumber"] not in roomcodes:
#				print(k["buildingCode"] + "-" + k["roomNumber"])
#				continue
			c = {}
			c["deptcode"] = i["subject"]
			c["department"] = list(filter(lambda x: x["code"] == i["subject"], subjects))[0]["description"]
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
			c["startTime"] = temp
			temp = str(temp)
			c["prettyStartTime"] = temp[:-2] + ":" + temp[-2:]
			temp = int(k["endTime"])
			if temp < 1200 and k["pmCode"] == "P":
				temp += 1200
			c["endTime"] = temp
			temp = str(temp)
			c["prettyEndTime"] = temp[:-2] + ":" + temp[-2:]
			if k["campusLocation"] == "1":
				c["campus"] = "CAC"
				if dumps(c, sort_keys=True) not in collegeaves:
					collegeaves.add(dumps(c, sort_keys=True))
					collegeave.insert(0,c)
			elif k["campusLocation"] == "2":
				c["campus"] = "BUS"
				if dumps(c, sort_keys=True) not in buschs:
					buschs.add(dumps(c, sort_keys=True))
					busch.insert(0,c)
			elif k["campusLocation"] == "3":
				c["campus"] = "LIV"
				if dumps(c, sort_keys=True) not in livis:
					livis.add(dumps(c, sort_keys=True))
					livi.insert(0,c)
			elif k["campusLocation"] == "4":
				c["campus"] = "CD"
				if dumps(c, sort_keys=True) not in cookdougs:
					cookdougs.add(dumps(c, sort_keys=True))
					cookdoug.insert(0,c)
			else:
				pprint(k["campusLocation"] + " " +  k["campusName"] + " " + j["index"])
				assert(False)
#			print(c)

busch = sorted(busch, key=lambda k: k['startTime'])
livi = sorted(livi, key=lambda k: k['startTime'])
cookdoug = sorted(cookdoug, key=lambda k: k['startTime'])
collegeave = sorted(collegeave, key=lambda k: k['startTime'])
data = {1 : collegeave, 3: livi, 4 : cookdoug, 2: busch}

print('adding classes to database')
cur.execute("TRUNCATE TABLE courses")
for d in data:
	for m in data[d]:
		cur.execute("INSERT INTO courses (title, room, department, day, startTime, endTime,building, deptcode, coursecode, campus) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (m["title"], m["room"], m["department"], m["day"], m["startTime"], m["endTime"], m["building"], m["deptcode"], m["coursecode"], m["campus"]))

conn.commit()
cur.close()
conn.close()

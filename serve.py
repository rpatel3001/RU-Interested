from flask import *
from flask_wtf import FlaskForm
from flask_bootstrap import Bootstrap
from wtforms import validators, TextField, IntegerField, SubmitField, SelectField, SelectMultipleField
from datetime import datetime
import psycopg2
import os
import urllib.parse as urlparse
import subprocess
import time

daysOfWeek = ["M","M","T","W","TH","F","S"]

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

app = Flask(__name__)
app.secret_key = "dsvasdvavasverbijbiujrenv0982ygf7328ibh"
Bootstrap(app)

cur.execute("SELECT * FROM rooms")
temp = cur.fetchall()
rooms = [dict(zip(("building","campus", "buildingcode", "roomnum", "capacity"),t)) for t in temp]
buildings = set([(x["building"], x["buildingcode"]) for x in rooms])
buildings = [{"name":x[0], "code":x[1]} for x in buildings]

cur.execute("SELECT * FROM departments")
temp = cur.fetchall()
departments = [dict(zip(("name","code"),t)) for t in temp]

def get_classes(campus, day, start, end, reqb=[''], reqs=['']):
	cur.execute("SELECT * FROM courses WHERE starttime BETWEEN %s AND %s AND campus = %s AND day = %s ", (start, end, campus, day))
	temp = cur.fetchall()
	classes = [dict(zip(("title","room","department","day","startTime","endTime", "building","deptcode","coursecode","campus"),r)) for r in temp]
	classes = [x for x in classes if (reqs == [''] or x["deptcode"] in reqs) and (reqb == [''] or x["building"] in reqb)]
	for c in classes:
		if c["startTime"] > 1300:
			c["startTime"] = str(c["startTime"]-1200)
			c["startTime"] = c["startTime"][:-2] + ":" + c["startTime"][-2:] + " PM"
		else:
			c["startTime"] = str(c["startTime"])
			c["startTime"] = c["startTime"][:-2] + ":" + c["startTime"][-2:] + " AM"
		if c["endTime"] > 1300:
			c["endTime"] = str(c["endTime"]-1200)
			c["endTime"] = c["endTime"][:-2] + ":" + c["endTime"][-2:] + " PM"
		else:
			c["endTime"] = str(c["endTime"])
			c["endTime"] = c["endTime"][:-2] + ":" + c["endTime"][-2:] + " AM"
	return classes

def get_buildings():
	return buildings

def get_departments():
	return departments

@app.route('/api')
def info():
	return render_template("api_info.html")

@app.route('/api/buildings')
def send_buildings():
	return jsonify(get_buildings())

@app.route('/api/departments')
def send_departments():
	return jsonify(get_departments())

@app.route('/api/classes/<string:campus>/<string:day>/<int:start>/<int:end>', methods=['GET'])
def send_classes(campus, day, start, end):
	return jsonify(get_classes(campus, day, start, end, request.args.get('buildings', default="").split(','), request.args.get('departments', default="").split(',')))

@app.route('/', methods=['GET', 'POST'])
def submit():
	form = SpecifierForm()
	if not form.building.data:
		form.building.data = ['']
	if not form.department.data:
		form.department.data = ['']
	classes = get_classes(form.campus.data, form.day.data, form.startTime.data, form.endTime.data)
	form.department.choices = [(x["code"], x["name"]) for x in departments if x["code"] in [y["deptcode"] for y in classes]]
	classes = [x for x in classes if form.department.data == [''] or x["deptcode"] in form.department.data]
	form.building.choices = [(b["code"], b["name"]) for b in buildings if b["code"] in [x["building"] for x in classes]]
	classes = [x for x in classes if form.building.data == [''] or x["building"] in form.building.data]
	return render_template("main.html", form=form, results=classes)

class SpecifierForm(FlaskForm):
	campus = SelectField('campus', choices=[("CAC", "College Avenue"), ("BUS", "Busch"), ("LIV", "Livingston"), ("CD", "Cook/Douglas")], default='CAC')
	building = SelectMultipleField("building")
	department = SelectMultipleField("department")
	times = [(800,"8:00 AM"),(830,"8:30 AM"),(900,"9:00 AM"),(930,"9:30 AM"),(1000,"10:00 AM"),(1030,"10:30 AM"),
			(1100,"11:00 AM"),(1130,"11:30 AM"),(1200,"12:00 PM"),(1230,"12:30 PM"),(1300,"1:00 PM"),(1330,"1:30 PM"),
			(1400,"2:00 PM"),(1430,"2:30 PM"),(1500,"3:00 PM"),(1530,"3:30 PM"),(1600,"4:00 PM"),(1630,"4:30 PM"),
			(1700,"5:00 PM"),(1730,"5:30 PM"),(1800,"6:00 PM"),(1830,"6:30 PM"),(1900,"7:00 PM"),(1930,"7:30 PM"),
			(2000,"8:00 PM"),(2030,"8:30 PM"),(2100,"9:00 PM"),(2130,"9:30 PM"),(2200,"10:00 PM"),(2230,"10:30 PM")]
	
	currDay = daysOfWeek[int(datetime.now().strftime("%w"))]
	currTime = int(int(datetime.now().strftime("%H%M")) / 100) * 100
	day = SelectField('startTime', choices=[("M", "Monday"),("T", "Tuesday"),("W", "Wednesday"),("TH", "Thursday"),("F", "Friday"),("S","Saturday")], default=currDay);
	startTime = SelectField('startTime', choices=times, default=currTime);
	endTime = SelectField('endTime', choices=times, default=currTime+130);

@app.route('/api/esp_report', methods=['POST'])
def esp_report():
	data = (float(request.values['temp']), float(request.values['hum']), float(request.values['pres']), float(request.values['down_speed']))
	cur.execute("INSERT INTO esp_data (temp, hum, pres, down_speed) VALUES (%f, %f, %f, %f)"%data)
	conn.commit()
	return jsonify(success=True)

@app.route('/api/esp_view')
def esp_view():
	cur.execute("SELECT * FROM esp_data WHERE time > (NOW() - INTERVAL '1 DAY') ORDER BY id DESC")
	ret = [dict(zip(['id', 'time', 'temp', 'hum', 'pres', 'down_speed'], x)) for x in cur.fetchall()][::-1]
	ids = [r['id'] for r in ret]
	temps = [r['temp'] for r in ret]
	hums = [r['hum'] for r in ret]
	press = [r['pres'] for r in ret]
	for r in ret:
		r['time'] = r['time'].strftime("%Y-%m-%dT%H:%M:%S")
	times = [r['time'] for r in ret]
	return render_template('esp_view.html', labels=times, temp=temps, hum=hums, pres=press)

@app.route('/api/updateblog', methods=['POST'])
def updateblog():
	subprocess.call(['rm', '-rf', 'output'], cwd='/opt/blog')
	subprocess.call(['git', 'pull'], cwd='/opt/blog')
	subprocess.call(['sudo', 'chown', '-R', 'rajan:rajan', '.'], cwd='/opt/blog')
	try:
		res = subprocess.check_output(['/usr/local/bin/pelican', '-vD', 'content'], cwd='/opt/blog')
		return res
	except CalledProcessError as e:
		return e.output


def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"%s error - %s" % (getattr(form, field).label.text, error))

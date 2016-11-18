from flask import Flask, render_template, flash, redirect
from flask_wtf import FlaskForm
from wtforms import SelectField, SelectMultipleField
from wtforms.validators import DataRequired
import json
from datetime import datetime
import psycopg2
import os
import urllib.parse as urlparse

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
	conn = psycopg2.connect("dbname=DATABASE user=postgres")

cur = conn.cursor()

app = Flask(__name__)
app.secret_key = "dsvasdvavasverbijbiujrenv0982ygf7328ibh"

cur.execute("SELECT * FROM buildings")
temp = cur.fetchall()
buildings = [dict(zip(("code","name","id"),t)) for t in temp]

@app.route('/', methods=['GET', 'POST'])
def submit():
	form = SpecifierForm()
	cur.execute("SELECT * FROM classes WHERE time BETWEEN %s AND %s AND campus = %s AND day = %s ", (form.startTime.data, form.endTime.data, form.campus.data, form.day.data))
	temp = cur.fetchall()
	classes = [dict(zip(("title","room","department","day","time","building","courseNum","campus"),r)) for r in temp]
	cur.execute("SELECT DISTINCT s.* FROM subjects s INNER JOIN classes c ON s.code=SUBSTRING(c.coursenum for 3)")
	temp = cur.fetchall()
	form.department.choices = [(b,a) for a,b, in temp]
	classes = [x for x in classes if (form.department.data == None or form.department.data == [] or x["courseNum"][:3] in form.department.data)]
	form.building.choices = [(b["code"], b["name"]) for b in buildings if b["code"] in [x["building"] for x in classes]]
	classes = [x for x in classes if (form.building.data == None or form.building.data == [] or not (set(form.building.data) <= set([z[0] for z in form.building.choices])) or x["building"] in form.building.data)]
	return render_template("main.html", form=form, results=classes)

class SpecifierForm(FlaskForm):
	campus = SelectField('campus', choices=[(1, "College Avenue"), (2, "Busch"), (3, "Livingston"), (4, "Cook/Douglas")], default=1)
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

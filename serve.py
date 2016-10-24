from flask import Flask, render_template, flash, redirect
from flask_wtf import FlaskForm
from wtforms import SelectField, SelectMultipleField
from wtforms.validators import DataRequired
from pprint import pprint
import json
from datetime import datetime

daysOfWeek = ["","M","T","W","TH","F","S"]

app = Flask(__name__)
app.secret_key = "dsvasdvavasverbijbiujrenv0982ygf7328ibh"
dataInFile = open("data.dat", "r")
dataIn = json.load(dataInFile)
dataInFile.close()
print("Data loaded")
classesInFile = open("classes.dat", "r")
classesIn = json.load(classesInFile)
classesInFile.close()
print("Class lists loaded")

@app.route('/', methods=['GET', 'POST'])
def submit():
	form = SpecifierForm()
	classes = [x for x in classesIn[form.campus.data]
				if x["time"] >= int(form.startTime.data)
					and x["time"] < int(form.endTime.data)
					and x["day"] == form.day.data]
	form.department.choices = set([(x["courseNum"][:3], [y["description"] for y in dataIn["subjects"] if y["code"] == x["courseNum"][:3]][0]) for x in classes])
	classes = [x for x in classes if (form.department.data == None or form.department.data == [] or x["courseNum"][:3] in form.department.data)]
	form.building.choices = [(x["code"], x["name"]) for x in dataIn["buildings"] if x["campus"] == form.campus.data and x["code"] in [x["building"] for x in classes]]
	classes = [x for x in classes if (form.building.data == None or form.building.data == [] or not (set(form.building.data) < set([z[0] for z in form.building.choices])) or x["building"] in form.building.data)]
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
	if currDay == "":
		currDay = "M"
	currTime = int(int(datetime.now().strftime("%H%M")) / 100) * 100
	day = SelectField('startTime', choices=[("M", "Monday"),("T", "Tuesday"),("W", "Wednesday"),("TH", "Thursday"),("F", "Friday"),("S","Saturday")], default=currDay);
	startTime = SelectField('startTime', choices=times, default=currTime);
	endTime = SelectField('endTime', choices=times, default=currTime+100);
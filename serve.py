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
	time = int(datetime.now().strftime("%H%M"))
	day = daysOfWeek[int(datetime.now().strftime("%w"))]
	form = SpecifierForm()
	classes = []
	if form.campus.data != "None":
		classes = [x for x in classesIn[form.campus.data] if x["time"] > time and x["day"] == "M"]																		
	form.building.choices = [(x["code"], x["name"]) for x in dataIn["buildings"] if x["campus"] == form.campus.data and x["code"] in [y["building"] for y in [w for z in classesIn for w in classesIn[z]]]]
	print(form.building.choices)
	return render_template("main.html", form=form, results=classes)

class SpecifierForm(FlaskForm):
	campus = SelectField('campus', choices=[(1, "College Avenue"), (2, "Busch"), (3, "Livingston"), (4, "Cook/Douglas")])
	building = SelectMultipleField("building")
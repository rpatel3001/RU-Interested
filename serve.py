from flask import Flask, render_template, flash, redirect
from flask_wtf import FlaskForm
from wtforms import SelectField, SelectMultipleField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.secret_key = "dsvasdvavasverbijbiujrenv0982ygf7328ibh"

@app.route('/')
def hello():
	return render_template("base.html")

@app.route('/submit', methods=['GET', 'POST'])
def submit():
	form = SpecifierForm()
	if form.validate_on_submit():
		form.campus.default = form.campus.value
		form.process()
	print(form.campus.data)
	return render_template("form.html", form=form)

class SpecifierForm(FlaskForm):
	campus = SelectField('campus', choices=[(1, "College Avenue"), (2, "Busch"), (3, "Livingston"), (4, "Cook/Douglas")])#, validators=[DataRequired()])
	building = SelectMultipleField("building", choices=[]);
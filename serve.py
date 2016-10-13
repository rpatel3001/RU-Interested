from flask import Flask, render_template
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired

app = Flask(__name__)

@app.route('/')
def hello_world():
    return render_template("form.html")

from app import flask_app
from flask import redirect, url_for, render_template

@flask_app.route('/login')
def login():
	return render_template('login.html')
	
@flask_app.route('/signup')
def signup():
	return render_template('signup.html')
	
@flask_app.route('/challenge')
def challenge():
	return render_template('challenge.html')

@flask_app.route('/welcome')
def welcome():
	return render_template('welcome.html')

@flask_app.route('/')
def index():
	return redirect(url_for('challenge'))

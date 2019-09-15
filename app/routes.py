from app import flask_app
from flask import redirect, url_for, render_template
from app.forms import WelcomeForm, SignupForm, LoginForm

@flask_app.route('/login', methods=['GET', 'POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		#login the user
		return redirect(url_for('challenge'))
	return render_template('login.html', form=form)
	
@flask_app.route('/signup', methods=['GET', 'POST'])
def signup():
	form = SignupForm()
	if form.validate_on_submit():
		#save data to Db
		#login user
		return redirect(url_for('challenge'))
	return render_template('signup.html', form=form)
	
@flask_app.route('/challenge')
def challenge():
	return render_template('challenge.html', room='test-room', user='test-user', text=sample_challenge['text'])

@flask_app.route('/welcome', methods=['GET', 'POST'])
def welcome():
	form = WelcomeForm()
	if form.validate_on_submit():
		create = form.create.data
		if create:
			return redirect(url_for('signup'))
		else:
			return redirect(url_for('login'))
	return render_template('welcome.html', form=form)

@flask_app.route('/')
def index():
	return redirect(url_for('welcome'))
	

@flask_app.route('/change_room')
def change_room():
	#logout user
	return redirect(url_for('welcome'))

sample_challenge = {"text": "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.", 
					"hints": ["Lorem ipsum dolor sit amet",
					"Ut enim ad minim veniam"]
					}

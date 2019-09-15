from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo


class WelcomeForm(FlaskForm):
	create = SubmitField('Create group')
	join = SubmitField('join group')
	
class SignupForm(FlaskForm):
	group_name = StringField('Group name', validators=[DataRequired()])
	group_psw = PasswordField('Group password', validators=[DataRequired(), EqualTo('confirm', message='The passwords must match')])
	confirm = PasswordField('Repeat password')
	username = StringField('Username', validators=[DataRequired()])
	create = SubmitField('Create and join group')
	
class LoginForm(FlaskForm):
	group_name = StringField('Group name', validators=[DataRequired()])
	group_psw = PasswordField('Group password', validators=[DataRequired()])
	username = StringField('Username', validators=[DataRequired()])
	join = SubmitField('Join group')
	
#add custom validators for Db elements
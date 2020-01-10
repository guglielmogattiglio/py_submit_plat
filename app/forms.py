from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo, ValidationError, Regexp
from app.models import Groups


class WelcomeForm(FlaskForm):
    create = SubmitField('Create group')
    join = SubmitField('join group')
    
class SignupForm(FlaskForm):
    regex = Regexp(r"^[-a-zA-Z0-9\s_]+$", message='Only letters, numbers, whitespaces, dashes and underscores allowed.')
    group_name = StringField('Group name', validators=[DataRequired(), regex])
    group_psw = PasswordField('Group password', validators=[DataRequired(),
                                                            EqualTo('confirm', message='The passwords must match'),
                                                            regex])
    confirm = PasswordField('Repeat password')
    create = SubmitField('Create and join group')
    
    #check group_name not taken
    def validate_group_name(self, group_name):
        name = Groups.query.filter_by(group_name=group_name.data).first()
        if name is not None:
            raise ValidationError('The group name chosen is already taken.')
    
class LoginForm(FlaskForm):
    group_name = StringField('Group name', validators=[DataRequired()])
    group_psw = PasswordField('Group password', validators=[DataRequired()])
    join = SubmitField('Join group')
    
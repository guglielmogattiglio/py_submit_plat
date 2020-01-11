from app import db
from flask_login import UserMixin
from app import login
from datetime import datetime

class Groups(db.Model):
    group_id = db.Column(db.Integer, primary_key=True)
    group_name = db.Column(db.String(64), index=True, unique=True, nullable=False)
    group_psw = db.Column(db.String(64), nullable=False)
    group_challenges = db.relationship("ChallengeGroup", cascade="all, delete-orphan", backref="group")
    
    def __repr__(self):
        return f'<group: {self.group_name}>'
    
class Challenges(db.Model):
    challenge_id = db.Column(db.Integer, primary_key=True)
    specification = db.Column(db.Text, nullable=False)
    allowed_functions = db.Column(db.Text, nullable=False)
    required_modules = db.Column(db.Text, nullable=False)
    solutions = db.Column(db.Text, nullable=False)
    func_name = db.Column(db.String(64), nullable=False)
    max_score = db.Column(db.Float(), nullable=False)
    weight = db.Column(db.Float(), nullable=False, default=1)
    is_simulation = db.Column(db.Boolean(), nullable=False, default=False)

    challenge_scoreboard = db.relationship("ChallengeGroup", cascade="all, delete-orphan", backref="challenge")
    def __repr__(self):
        return f'<Challenge {self.challenge_id}>'
    

class ChallengeGroup(db.Model):
    group_id = db.Column(db.Integer, db.ForeignKey('groups.group_id'), primary_key=True)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenges.challenge_id'), primary_key=True)
    n_attempts = db.Column(db.Integer, nullable=False)
    best_score = db.Column(db.Float(), nullable=False)
    last_score = db.Column(db.Float(), nullable=False)
          
    
class Users(db.Model, UserMixin):
    user_id = db.Column(db.BigInteger, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.group_id'))
    group = db.relationship("Groups", backref="users")
    
    #works because class instance keeps initial assignments
    #i.e. self.user_id = user_id
    def get_id(self):
        return str(self.user_id)
    
@login.user_loader
def load_user(id):
    return Users.query.get(int(id))

class Submissions(db.Model):
    submission_id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.group_id'))
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenges.challenge_id'))
    submission_time = db.Column(db.DateTime, nullable=False, default=datetime.now)
    code = db.Column(db.Text, nullable=False)
    score = db.Column(db.Float(), nullable=False)
    output_result = db.Column(db.Text, nullable=False)
    has_raised_exc = db.Column(db.Boolean, nullable=False)    

    

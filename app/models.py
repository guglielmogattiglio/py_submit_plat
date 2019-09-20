from app import db
from flask_login import UserMixin
from app import login

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
    challenge_scoreboard = db.relationship("ChallengeGroup", cascade="all, delete-orphan", backref="challenge")
    def __repr__(self):
        return f'<Challenge {self.challenge_id}>'
    

class ChallengeGroup(db.Model):
    group_id = db.Column(db.Integer, db.ForeignKey('groups.group_id'), primary_key=True)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenges.challenge_id'), primary_key=True)
    n_attempts = db.Column(db.Integer, nullable=False)
    best_score = db.Column(db.Integer, nullable=False)
    last_score = db.Column(db.Integer, nullable=False)
          
    
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

    

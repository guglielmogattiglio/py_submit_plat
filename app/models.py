from app import db

class Groups(db.Model):
    group_id = db.Column(db.Integer, primary_key=True)
    group_name = db.Column(db.String(64), index=True, unique=True, nullable=False)
    group_psw = db.Column(db.String(64), nullable=False)
    connected_users = db.Column(db.Integer)
    group_challenges = db.relationship("ChallengeGroup", cascade="all, delete-orphan", backref="group")
    
    def __repr__(self):
        return f'<group: {self.group_name}>'
    
class Challenges(db.Model):
    challenge_id = db.Column(db.Integer, primary_key=True)
    max_score = db.Column(db.Integer)
    challenge_scoreboard = db.relationship("ChallengeGroup", cascade="all, delete-orphan", backref="challenge")
    def __repr__(self):
        return f'<Challenge {self.challenge_id}>'
    

class ChallengeGroup(db.Model):
    group_id = db.Column(db.Integer, db.ForeignKey('groups.group_id'), primary_key=True)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenges.challenge_id'), primary_key=True)
    n_attempts = db.Column(db.Integer)
    best_score = db.Column(db.Integer)
    last_score = db.Column(db.Integer)
          
    

    

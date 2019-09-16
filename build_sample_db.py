from app import db
from app.models import Groups, Challenges, ChallengeGroup

#empty db
Groups.query.delete()
Challenges.query.delete()
ChallengeGroup.query.delete()
db.session.commit()

#populate db
g1 = Groups(group_id=1, group_name='my_first', group_psw='psw_1', connected_users=0)
g2 = Groups(group_id=2, group_name='my_second', group_psw='psw_2')
g3 = Groups(group_id=3, group_name='my_third', group_psw='psw_3')
g4 = Groups(group_name='my_forth', group_psw='psw_3')

db.session.add_all([g1, g2, g3, g4])
db.session.commit()

c1 = Challenges(challenge_id=1, max_score=0)
c2 = Challenges(challenge_id=2, max_score=100)
c3 = Challenges(challenge_id=3)

db.session.add_all([c1, c2, c3])
db.session.commit()

c_g1 = ChallengeGroup(group_id=1, challenge_id=1, n_attempts=20)
c_g2 = ChallengeGroup(group_id=1, challenge_id=2, n_attempts=2, best_score=0)
c_g3 = ChallengeGroup(group_id=1, challenge_id=3, n_attempts=1, best_score=6)
c_g4 = ChallengeGroup(group_id=2, challenge_id=1, n_attempts=11, best_score=4)

db.session.add_all([c_g1, c_g2, c_g3, c_g4])
db.session.commit()


#print(Groups.query.all())
#print(Challenges.query.all())
#print(ChallengeGroup.query.all())
#
#print(Groups.query.join(ChallengeGroup, Groups.group_id == ChallengeGroup.group_id).all())
#
#result = Challenges.query.all()
#for challenge in result:
#    print([gc.group for gc in challenge.challenge_scoreboard])
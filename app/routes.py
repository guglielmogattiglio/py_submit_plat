from app import flask_app, db, socketio
from flask import redirect, url_for, render_template, flash
from app.forms import WelcomeForm, SignupForm, LoginForm
from app.models import Groups, Users, Challenges, ChallengeGroup
from flask_login import login_user, current_user, logout_user, login_required
from flask_socketio import emit, join_room, leave_room, disconnect

import threading
import traceback
import random

thread = None
thread_lock = threading.Lock()


@flask_app.route('/')
def index():
    return redirect(url_for('welcome'))



@flask_app.route('/welcome', methods=['GET', 'POST'])
def welcome():
    if current_user.is_authenticated:
        my_logout_user()
    form = WelcomeForm()
    if form.validate_on_submit():
        create = form.create.data
        if create:
            return redirect(url_for('signup'))
        else:
            return redirect(url_for('login'))
    return render_template('welcome.html', form=form)


@flask_app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        my_logout_user()
    form = SignupForm()
    if form.validate_on_submit():
        #save data to Db
        new_group = Groups(group_name=form.group_name.data, group_psw=form.group_psw.data)
        db.session.add(new_group)
        db.session.commit()
        #load group from db, needed for group_id
        group = Groups.query.filter_by(group_name=form.group_name.data).first()
        #login user
        my_login_user(group)
        return redirect(url_for('challenge'))
    return render_template('signup.html', form=form)



@flask_app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        my_logout_user()
    form = LoginForm()
    if form.validate_on_submit():
        #check credentials
        group = Groups.query.filter_by(group_name=form.group_name.data).first()
        if group is None or group.group_psw != form.group_psw.data:
            flash('Invalid group name or password.')
            return redirect(url_for('login'))
        else:
            #login user
            my_login_user(group)
            return redirect(url_for('challenge'))
    return render_template('login.html', form=form)
    

    

@flask_app.route('/challenge')
@login_required
def challenge():
    group = current_user.group.group_name
    n_users = len(current_user.group.users)
    return render_template('challenge.html', group=group, n_users=n_users, text=sample_challenge['text'], high_score_1=7, redirect=url_for('welcome'))


@socketio.on('connect')
def on_connect():
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(push_updates)
            

def push_updates(): 
    '''
    Be VERY VERY careful in thread because if you use relationship shortcuts like 
    group.users it will not work (doesn't update w.r.t. main thread)
    '''
    while True:
        socketio.sleep(3) 
        if Users.query.first() is not None: #there are conn users
            groups = Groups.query.all()
            for group in groups: #need to update all groups...
                n_users = len(db.session.query(Users.user_id).filter_by(group_id=group.group_id).join(Groups).all())
                if n_users > 0:             #... but only if active
                    print(group.group_name, n_users)
                    socketio.emit('update_n_users', 
                          {'n_users': n_users}, room=group.group_name)
                    
            #update leatherboard TODO:test it
            challenges = Challenges.query.order_by(Challenges.challenge_id).all()
            result = [[(c_group[1].group.group_name, c_group[1].last_score) for c_group in \
                       db.session.query(Challenges, ChallengeGroup).filter_by(challenge_id=c.challenge_id).\
                       join(Challenges).order_by(ChallengeGroup.last_score.desc()).limit(3).all()] for c in challenges]
            socketio.emit('update_scoreboard', result, broadcast=True)
            
            

@socketio.on('process_script')
def process_script(json): #TODO: yet to be tested
    if current_user.get_id() is None:
        raise Exception('exc_1')
    #need filling: convert input, evaluate code, update db with score, return feedback
    script, c_id, group_name = extract_script(json)
    try:
        score = evaluate_script(script)
        group = Groups.query.filter_by(group_name=group_name).first()
        record = ChallengeGroup.query.get((group.group_id, c_id))
        if record is None:
            db.session.add(ChallengeGroup(group_id=group.group_id, challenge_id=c_id, 
                                          n_attempts=1, best_score=score, last_score=score))
        else:
            record.n_attempts += 1
            record.last_score = score
            if record.best_score < score:
                record.best_score = score
            db.session.commit()
        emit('feedback', {'score': score, 'output': f'Your new score is {score}'})
    except:
        output = traceback.format_exc()
        emit('feedback', {'score': 0, 'output': output})
    
    
def extract_script(json):
    script = json['script']
    c_id = json['challenge_id']
    group_name = json['group']
    return script, c_id, group_name


def evaluate_script(script):
    return 3
        

@socketio.on('change_group')
def return_home(msg):
     my_logout_user()
     emit('redirect', {})
    
@socketio.on('join')
def on_join(data):
    group_name = data['group']
    join_room(group_name)
    
    
@socketio.on('disconnect')
def on_disconnect():
    if current_user.is_authenticated:
        #leave room
        group_name = current_user.group.group_name
        leave_room(group_name)
        #logout user
        my_logout_user()
    
    


def my_login_user(group):
    #add random to prevent zombie users i.e. users that can connect to challenge but are
    #not recognized by server, that is because the session token is kept by the browser and 
    #when the webpage is closed without logging out, the token is not removed and when it reappears
    #it has the same id as before, which possibly has been assigned to another (so can't detect
    #it by checking for current_user.get_id() is None and the server realizes it is the same user that just opened a new webapge). 
    #By giving random numbers as ID i'm preventing this
    user = Users(user_id=random.randint(1,90000000000000), group_id=group.group_id)
    print('logged in user with group_id', group.group_id)
    db.session.add(user)
    db.session.commit()
    login_user(user, remember=True)
    
    
def my_logout_user():
    user = current_user
    Users.query.filter_by(user_id=int(user.get_id())).delete()
    db.session.commit()
    logout_user()
    return redirect(url_for('welcome'))

sample_challenge = {"text": "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.", 
                    "hints": ["Lorem ipsum dolor sit amet",
                    "Ut enim ad minim veniam"]
                    }

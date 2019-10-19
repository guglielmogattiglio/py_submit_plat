from app import flask_app, db, socketio
from flask import redirect, url_for, render_template, flash
from app.forms import WelcomeForm, SignupForm, LoginForm
from app.models import Groups, Users, Challenges, ChallengeGroup, Submissions
from flask_login import login_user, current_user, logout_user, login_required
from flask_socketio import emit, join_room, leave_room, disconnect
import db_connection as db_pymysql

import threading
import traceback
import random
import re
import ast
import logging
import func_timeout

thread = None
thread_lock = threading.Lock()


@flask_app.route('/')
def index():
    return redirect(url_for('welcome'))



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


@flask_app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        flash('Cannot create group as you are already logged in. Change group first.')
        return redirect(url_for('challenge'))
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
        flash('Cannot create group as you are already logged in. Change group first.')
        return redirect(url_for('challenge'))
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
    group = Groups.query.filter_by(group_id=int(current_user.group_id)).first().group_name
    n_users = len(current_user.group.users)
    challenges = Challenges.query.all()
    msg = []
    for c in challenges:
        msg.append(ast.literal_eval(c.specification))
    return render_template('challenge.html', group=group, n_users=n_users, msg=msg, redirect=url_for('welcome'), id=current_user.get_id())


@socketio.on('connect')
def on_connect():
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(push_updates)
            

def push_updates(): 
    '''
    Be VERY VERY careful in thread because if you use sqlalchemy relationship shortcuts like 
    group.users it will not work (doesn't update w.r.t. main thread)
    '''
    while True:
        socketio.sleep(3) 
        if db_pymysql.check_users_connected(): #there are conn users
            groups = db_pymysql.get_groups()
            for group in groups: #need to update all groups...
                n_users = db_pymysql.get_n_users(group['group_id'])
                if n_users > 0:             #... but only if active
                    socketio.emit('update_n_users', 
                          {'n_users': n_users}, room=group['group_name'])
                    
            #update leatherboard 
            challenges = db_pymysql.get_ordered_challenge_id()
            result = [[(group['group_name'], group['last_score']) for group in db_pymysql.get_top_3_groups(c['challenge_id'])] for c in challenges]
            socketio.emit('update_scoreboard', result, broadcast=True)
            
            

@socketio.on('process_script')
def process_script(json): 
    if current_user.get_id() is None:
        emit('redirect', {})
    
    orig_script, c_id, group_name = extract_script(json)
    #fetch from db
    ch = Challenges.query.filter_by(challenge_id=c_id).first()
    safe_dict = make_safe_dict(ch.allowed_functions, ch.required_modules)
    has_raised_exc = False
    try:
        script = validate_script(orig_script)
        score, outcome, outcome_short = evaluate_script(script, safe_dict, ch.func_name, ch.solutions)
        output = f'Your new score is {score}\n' + "\n".join(outcome)
    except Exception as e:
        logging.error("Error for user: %s\n" % current_user.get_id() + traceback.format_exc())
        output = "Error for user: %s\n" % current_user.get_id() + str(e)
        score = 0
        has_raised_exc = True
        outcome_short = []
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
    
    #log uploaded data to db
    submission = Submissions(group_id=group.group_id, challenge_id=c_id, code=orig_script,
                             score=score, output_result=",".join(map(str, outcome_short)), has_raised_exc=has_raised_exc)
    db.session.add(submission)
    db.session.commit()
    
    emit('feedback', {'score': score, 'output': output, 'c_id': c_id})
    
    
def extract_script(json):
    script = json['script']
    c_id = json['challenge_id']
    group_name = json['group']
    return script, c_id, group_name

def make_safe_dict(allowed_functions, required_modules):
    safe_dict = {}
    exec(required_modules)
    for f in ast.literal_eval(allowed_functions):
        f_name = extract_f_name(f)
        safe_dict[f_name] = eval(f)
        safe_dict[f] = eval(f)
    return safe_dict

def extract_f_name(f):
    i = f.find('.')
    while i >= 0:
        f = f[i+1:]
        i = f.find('.')
    return f

def validate_script(script):
    #first remove import
    script = re.sub(r'from.*?import.*|import.*', '', script)
    #remove comments (validated keywords could be contained inside)
    script = re.sub(r'#.*', '', script)
    script = re.sub(r"'''.*?'''", '', script, flags=re.S)   
    #prevent from exploiting eval
    if '__' in script:
        raise Exception('You are not allowed to use/call reserved names delimited by __')           
    return script

def evaluate_script(script, safe_dict, func_name, sol):
    no_builtins_dic = {"__builtins__" : None}
    safe_dict.update(no_builtins_dic) #keys already existing will be overwritten
    local = {}
    
    comp_code = compile(script, '<string>', 'exec')
    exec(comp_code, safe_dict, local)
    
    sol = ast.literal_eval(sol)
    outcome = []
    outcome_short = [] #1=pass, 0=fail, -1=timed-out
    score = 0
    c = 1
    for test in sol:
        try:
            ret_value = func_timeout.func_timeout(1, local[func_name], args=test[0])
            if ret_value == test[1]:
                outcome.append(f'test {c}: passed')
                outcome_short.append(1)
                score += 1
            else:
                outcome.append(f'test {c}: failed')
                outcome_short.append(0)
        except KeyError:
            raise Exception('KeyError raised during execution. Check that your function is called %s.\nIf that is correct, it is something within your code, for example check that all dictionaries operations work as expected.'%func_name) from None
        except TypeError as e:
            raise Exception(str(e)) from None
        except func_timeout.exceptions.FunctionTimedOut:
            outcome.append(f'test {c}: timed out')
            outcome_short.append(-1)
        except:
            raise
        c += 1
    return score, outcome, outcome_short
        

@socketio.on('change_group')
def return_home(msg):
    if current_user.get_id() is None:
        emit('redirect', {})
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
    db.session.add(user)
    db.session.commit()
    login_user(user, remember=True)
    
    
def my_logout_user():
    user = current_user
    Users.query.filter_by(user_id=int(user.get_id())).delete()
    db.session.commit()
    logout_user()
    return redirect(url_for('welcome'))

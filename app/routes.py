from app import flask_app, db, socketio
from flask import redirect, url_for, render_template, flash
from app.forms import WelcomeForm, SignupForm, LoginForm
from app.models import Groups, Users, Challenges, ChallengeGroup
from flask_login import login_user, current_user, logout_user, login_required
from flask_socketio import emit, join_room, leave_room, disconnect

import threading
import traceback
import random
import re
import ast

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
        if Users.query.first() is not None: #there are conn users
            groups = Groups.query.all()
            for group in groups: #need to update all groups...
                n_users = len(db.session.query(Users.user_id).filter_by(group_id=group.group_id).join(Groups).all())
                if n_users > 0:             #... but only if active
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
        emit('redirect', {})
    
    script, c_id, group_name = extract_script(json)
    #fetch from db
    ch = Challenges.query.filter_by(challenge_id=c_id).first()
    safe_dict = make_safe_dict(ch.allowed_functions, ch.required_modules)
    script = validate_script(script)
    try:
        score = evaluate_script(script, safe_dict, ch.func_name, ch.solutions)
        output = f'Your new score is {score}'
    except Exception as e:
        print(traceback.format_exc())
        output = "Error for user: %s\n" % current_user.get_id() + str(e)
        score = 0
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
    emit('feedback', {'score': 0, 'output': output, 'c_id': c_id})
    
    
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
    c = 0
    for test in sol:
        try:
            if local[func_name](*test[0]) == test[1]:
                c += 1
        except KeyError:
            raise Exception('KeyError raised during execution. Check that your function is called %s.\nIf that is correct, it is something within your code, for example check that all dictionaries operations work as expected.'%func_name) from None
        except TypeError as e:
            raise Exception(str(e)) from None
        except:
            raise
    return c
        

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

my_challenges = [{'id': 1, 'title': 'The + Operation', 
                 'text': 'Learn how to code summation in Python. The function you have to write takes two numeric inputs and returns their sum.', 
                 'max_score': 5, 'tips': ['No tips for this exercise, it is straightforward']},
                 {'id': 2, 'title': 'Reverse Me', 
                  'text': 'You have to write a function that given a strings, it reverses it. <br>For example, the word <i>python</i> would become <i>nohtyp</i>. The output needs to be in lowercase letters with no additional whitespaces.', 
                  'max_score': 8, 'tips': ['What if the initial string has an uppercase letter?', 'Note that the string itself may include whitespaces, in that case you have to leave them!']},
                 {'id': 3, 'title': 'title_3', 'text': 'text_3', 'max_score': 'max_score_3', 'tips': []},
                 {'id': 4, 'title': 'title_4', 'text': 'text_4', 'max_score': 'max_score_4', 'tips': ['tip*4_1', 'tip*4_2', 'tip*4_3', 'tip*4_4']}
                 ]

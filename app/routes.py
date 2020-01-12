from app import flask_app, db, socketio
from flask import redirect, url_for, render_template, flash, request
from app.forms import WelcomeForm, SignupForm, LoginForm
from app.models import Groups, Users, Challenges, ChallengeGroup, Submissions
from flask_login import login_user, current_user, logout_user, login_required
from flask_socketio import emit, join_room, leave_room, disconnect
import db_connection as db_pymysql
from config import Config
import script

import threading
import traceback
import random
import ast
import logging

thread = None
thread_lock = threading.Lock()
challenge_status = 'DC'  # DC= challenge is happening AC=finished, show recap


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
        # save data to Db
        new_group = Groups(group_name=form.group_name.data, group_psw=form.group_psw.data)
        db.session.add(new_group)
        db.session.commit()
        # load group from db, needed for group_id
        group = Groups.query.filter_by(group_name=form.group_name.data).first()
        # login user
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
        # check credentials
        group = Groups.query.filter_by(group_name=form.group_name.data).first()
        if group is None:
            flash("The group name doesn't exists.")
            return redirect(url_for('login'))
        elif group.group_psw != form.group_psw.data:
            flash('Wrong password for given user name.')
            return redirect(url_for('login'))
        else:
            # login user
            my_login_user(group)
            return redirect(url_for('challenge'))
    return render_template('login.html', form=form)


@flask_app.route('/challenge')
@login_required
def challenge():
    # check if client wants to connect as master
    master_pass = request.args.getlist('master_pass')
    if len(master_pass) != 0 and master_pass[0] == Config.MASTER_PASS:
        return render_template('challenge_master.html')

    group = Groups.query.filter_by(group_id=int(current_user.group_id)).first().group_name
    n_users = len(current_user.group.users)
    query = Challenges.query.with_entities(Challenges.challenge_id, Challenges.max_score, Challenges.is_simulation, Challenges.title) \
                      .filter(Challenges.challenge_id != -1).all()
    max_scores = {id: max_score for id, max_score, _, _ in query}
    is_sim = {id: is_sim for id, _, is_sim, _ in query}
    ch_names = {id: name for id, _, _, name in query}
    return render_template('challenge.html', group=group, n_users=n_users, redirect=url_for('welcome'),
                           id=current_user.get_id(), max_scores=max_scores, is_sim=is_sim, ch_names=ch_names)


@socketio.on('connect')
def on_connect():
    global thread, challenge_status
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(push_updates)

    if challenge_status == 'DC':
        challenges = Challenges.query.order_by('challenge_id').all()
        msg = []
        for c in challenges:
            msg.append(ast.literal_eval(c.specification))
        emit('load_during_challenge', msg)
    elif challenge_status == 'AC':
        emit('load_after_challenge')


def push_updates():
    while True:
        socketio.sleep(5)
        if db_pymysql.check_users_connected():  # there are conn users
            conn_users = db_pymysql.get_conn_users()
            for group in conn_users:  # need to update all groups...
                n_users = group['n_users']
                assert n_users > 0
                socketio.emit('update_n_users',
                              {'n_users': n_users}, room=group['group_name'])

            socketio.sleep(0)  # let server handle other tasks as this may take a while

            # update leatherboard
            result = db_pymysql.get_all_results()
            socketio.emit('update_scoreboard', result, broadcast=True)


######## Master Events #############


@socketio.on('end_challenge')
def end_challenge():
    global challenge_status
    challenge_status = 'AC'
    socketio.emit('load_after_challenge', broadcast=True)


@socketio.on('restart_challenge')
def restart_challenge():
    global challenge_status
    challenge_status = 'DC'
    challenges = Challenges.query.order_by('challenge_id').all()
    msg = []
    for c in challenges:
        msg.append(ast.literal_eval(c.specification))
    socketio.emit('load_during_challenge', msg, broadcast=True)


######## Slave Events ##############

@socketio.on('process_script')
def process_script(json):
    if current_user.get_id() is None:
        emit('redirect', {})

    orig_code, c_id, group_name = script.extract_script(json)
    # fetch from db
    ch = Challenges.query.filter_by(challenge_id=c_id).first()
    safe_dict = script.make_safe_dict(ch.allowed_functions, ch.required_modules)
    has_raised_exc = False
    try:
        code = script.validate_script(orig_code)
        process = script.evaluate_script(code, safe_dict, ch.func_name, ch.solutions, socketio.sleep,
                                         Config.TEST_CASE_TIMEOUT, ch.max_score, ch.is_simulation)
        for score, outcome, outcome_short in process:
            socketio.emit('feedback', {'score': score, 'output': "\n".join(outcome), 'c_id': c_id, 'is_last': False}, room=request.sid)
        output = "\n".join(outcome)
    except Exception as e:
        logging.error("Error for user: %s\n" % current_user.get_id() + traceback.format_exc())
        output = "Error for user: %s\n" % current_user.get_id() + str(e)
        score = 0
        has_raised_exc = True
        outcome_short = []
    if ch.is_simulation:
        score = truncate(score, 4)
    else:
        score = truncate(score * ch.weight, 4)
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

    # log uploaded data to db
    submission = Submissions(group_id=group.group_id, challenge_id=c_id, code=orig_code,
                             score=score, output_result=",".join(map(str, outcome_short)),
                             has_raised_exc=has_raised_exc)
    db.session.add(submission)
    db.session.commit()

    emit('feedback', {'score': score, 'output': output, 'c_id': c_id, 'is_last': True})


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
        # leave room
        group_name = current_user.group.group_name
        leave_room(group_name)
        # logout user
        my_logout_user()


def my_login_user(group):
    # add random to prevent zombie users i.e. users that can connect to challenge but are
    # not recognized by server, that is because the session token is kept by the browser and
    # when the webpage is closed without logging out, the token is not removed and when it reappears
    # it has the same id as before, which possibly has been assigned to another (so can't detect
    # it by checking for current_user.get_id() is None and the server realizes it is the same user that just opened a new webapge).
    # By giving random numbers as ID i'm preventing this
    user = Users(user_id=random.randint(1, 90000000000000), group_id=group.group_id)
    db.session.add(user)
    db.session.commit()
    login_user(user, remember=True)


def my_logout_user():
    user = current_user
    Users.query.filter_by(user_id=int(user.get_id())).delete()
    db.session.commit()
    logout_user()
    return redirect(url_for('welcome'))


########### Helper Functions #############

def truncate(x, digits):
    return int(10 ** digits * x) / 10 ** digits

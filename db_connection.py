import pymysql
from config import Config

login_data = Config.PYMYSQL_LOGIN_DATA

def connect():
    return pymysql.connect(user=login_data['user'], password=login_data['password'], host=login_data['host'], port=login_data['port'], database=login_data['database'])


def get_users():
    conn = connect()
    cursor = conn.cursor()
    sql = "select * from users"
    cursor.execute(sql)
    records = cursor.fetchall()
    if records is None:
        return None
    temp = [i for i in records]
    return temp

def check_users_connected():
    conn = connect()
    cursor = conn.cursor()
    sql = "select * from users limit 1"
    cursor.execute(sql)
    records = cursor.fetchall()
    if records is not None:
        return True
    return False

def get_groups():
    conn = connect()
    cursor = conn.cursor()
    sql = "select group_id, group_name from groups"
    cursor.execute(sql)
    records = cursor.fetchall()
    if records is None:
        return None
    result = [{'group_id': i[0], 'group_name': i[1]} for i in records]
    return result

def get_n_users(group_id):
    conn = connect()
    cursor = conn.cursor()
    sql = "select count(*) as n_users from users as u inner join (select g.group_id from groups as g where g.group_id=%s) as gr_filtered on u.group_id=gr_filtered.group_id"
    cursor.execute(sql, (group_id,))
    records = cursor.fetchall()
    if records is None:
        return None
    return records[0][0]

def get_ordered_challenge_id():
    conn = connect()
    cursor = conn.cursor()
    sql = "select c.challenge_id from challenges as c order by c.challenge_id asc"
    cursor.execute(sql)
    records = cursor.fetchall()
    if records is None:
        return None
    result = [{'challenge_id': i[0]} for i in records]
    return result

def get_top_3_groups(challenge_id):
    conn = connect()
    cursor = conn.cursor()
    sql = "select g.group_name, c_g_filt.last_score from groups as g inner join (select c_g.group_id, c_g.last_score from challenge_group as c_g where c_g.challenge_id=%s order by c_g.last_score desc limit 3) as c_g_filt on g.group_id=c_g_filt.group_id order by c_g_filt.last_score desc"
    cursor.execute(sql, (challenge_id,))
    records = cursor.fetchall()
    if records is None:
        return None
    result = [{'group_name': i[0], 'last_score': i[1]} for i in records]
    return result

def get_conn_users():
    conn = connect()
    cursor = conn.cursor()
    sql = "select res.n_users, group_name from (select count(*) as n_users, group_id from users group by group_id having count(*) > 0) as res inner join groups on res.group_id=groups.group_id"
    cursor.execute(sql)
    records = cursor.fetchall()
    if records is None:
        return None
    result = [{'n_users': i[0], 'group_name': i[1]} for i in records]
    return result

def get_all_results():
    conn = connect()
    cursor = conn.cursor()
    sql = "select g.group_name, c.challenge_id, c.n_attempts, c.best_score, c.last_score from challenge_group as c inner join groups as g on c.group_id=g.group_id order by c.challenge_id asc, c.last_score desc"
    cursor.execute(sql)
    records = cursor.fetchall()
    if records is None:
        return None
    result = [{'group_name': i[0], 'challenge_id': i[1], 'n_attempts': i[2], 'best_score': i[3], 'last_score': i[4]} for i in records]
    return result

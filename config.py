import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'my_secret_key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    PYMYSQL_LOGIN_DATA = {'user': os.environ.get('user'), 
                          'password': os.environ.get('password'), 
                          'host': os.environ.get('host'), 
                          'port': int(os.environ.get('port')),
                          'database': os.environ.get('database')}
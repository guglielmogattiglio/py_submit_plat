from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_socketio import SocketIO
from flask_bootstrap import Bootstrap
from sqlalchemy_utils import database_exists

flask_app = Flask(__name__)
flask_app.config.from_object(Config)
db = SQLAlchemy(flask_app)
migrate = Migrate(flask_app, db)
login = LoginManager(flask_app)
login.login_view = 'welcome'
socketio = SocketIO(flask_app)
bootstrap = Bootstrap(flask_app)

#to remove, init sample db
#import build_sample_db
if database_exists(Config.SQLALCHEMY_DATABASE_URI):
    import setup_db
else:
    print("WARNING: database not connected")

#here you can pre-load challenges and store them in db

from app import routes, models
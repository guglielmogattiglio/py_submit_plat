from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

flask_app = Flask(__name__)
flask_app.config.from_object(Config)
db = SQLAlchemy(flask_app)
migrate = Migrate(flask_app, db)

#to remove, init sample db
import build_sample_db

from app import routes, models
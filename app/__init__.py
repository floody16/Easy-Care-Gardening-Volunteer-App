from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'
login.login_message = 'You must be logged in to do that.'
login.login_message_category = 'danger'

from app import routes, models
from app.utils import usertype_pretty, timepref_pretty, timestamp_pretty

app.jinja_env.globals.update(usertype_pretty=usertype_pretty,
                             timepref_pretty=timepref_pretty,
                             timestamp_pretty=timestamp_pretty)
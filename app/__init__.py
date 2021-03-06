from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

login = LoginManager(app)
login.login_view = 'user.login'
login.login_message = 'Please log in first.'
login.login_message_category = 'danger'

address = app.config['ADDRESS']

from app import models
from app.utils import user_type_pretty, time_pref_pretty, timestamp_pretty, day_prefs_pretty
from app.views import auth, invite, user, job, news, manage

app.register_blueprint(auth.auth)
app.register_blueprint(invite.invite)
app.register_blueprint(user.user)
app.register_blueprint(job.job)
app.register_blueprint(news.news)
app.register_blueprint(manage.manage)

app.jinja_env.globals.update(user_type_pretty=user_type_pretty,
                             time_pref_pretty=time_pref_pretty,
                             day_prefs_pretty=day_prefs_pretty,
                             timestamp_pretty=timestamp_pretty)

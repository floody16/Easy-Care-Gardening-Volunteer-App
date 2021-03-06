from app import db, login
from enum import Enum

import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class UserType(Enum):
    VOLUNTEER = 0
    TEAM_LEADER = 1
    COORDINATOR = 2
    ADMINISTRATOR = 3

    def __str__(self):
        return {
            0: 'Volunteer',
            1: 'Team Leader',
            2: 'Coordinator',
            3: 'Administrator'
        }.get(self.value)


class DayPreference(Enum):
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5

    def __str__(self):
        return {
            0: 'Monday',
            1: 'Tuesday',
            2: 'Wednesday',
            3: 'Thursday',
            4: 'Friday',
            5: 'Saturday'
        }.get(self.value)


class TimePreference(Enum):
    HALF_DAY_MORNING = 'AM'
    HALF_DAY_AFTERNOON = 'PM'
    FULL_DAY = 'AP'

    def __str__(self):
        return {
            'AM': 'Half-day (Morning)',
            'PM': 'Half-day (Afternoon)',
            'AP': 'Full-day',
        }.get(self.value)


@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    full_name = db.Column(db.String(64))
    user_type = db.Column(db.Integer)
    password_hash = db.Column(db.String(128))
    time_pref = db.Column(db.String(2))
    day_pref = db.Column(db.String(6))
    join_date = db.Column(db.DateTime)
    next_police_check = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow())

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class NewsItem(db.Model):
    __tablename__ = 'news_item'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    title = db.Column(db.String(64))
    body = db.Column(db.String(2048))
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow())

    author = db.relationship('User', backref='news_item')
    acknowledgements = db.relationship('NewsItemAcknowledgement', backref='news_item', lazy='dynamic', cascade="all, delete, delete-orphan")

    def get_acknowledgements(self, news_item_id):
        return self.acknowledgements.filter_by(news_item_id=news_item_id).order_by(NewsItemAcknowledgement.created_at).all()

    def is_acknowledged(self, user_id):
        return self.acknowledgements.filter_by(user_id=user_id).count() > 0


class NewsItemAcknowledgement(db.Model):
    __tablename__ = 'acknowledgement'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    news_item_id = db.Column(db.Integer, db.ForeignKey('news_item.id'))
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow())

    acknowledger = db.relationship('User', backref='news_item_acknowledgement')


class Job(db.Model):
    __tablename__ = 'job'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    address = db.Column(db.String(64))
    date = db.Column(db.DateTime)
    time = db.Column(db.String(2))
    notes = db.Column(db.String(1024))
    cancelled = db.Column(db.Boolean, default=0)
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    author = db.relationship('User', backref='job')
    opt_ins = db.relationship('OptIn', backref='job', lazy='dynamic')
    feedback = db.relationship('Feedback', backref='job', lazy='dynamic')

    @staticmethod
    def get_past_jobs():
        return Job.query.filter(Job.date < datetime.datetime.utcnow()).all()

    def get_opt_ins(self, job_id):
        return self.opt_ins.filter_by(job_id=job_id).order_by(OptIn.created_at).all()

    def opted_into(self, user_id):
        return self.opt_ins.filter_by(user_id=user_id).order_by(OptIn.created_at).count() > 0

    def get_feedback(self, job_id):
        return self.feedback.filter_by(job_id=job_id).order_by(Feedback.created_at).all()


class OptIn(db.Model):
    __tablename__ = 'opt_in'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'))
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow())

    opter = db.relationship('User', backref='opt_in')


class Feedback(db.Model):
    __tablename__ = 'feedback'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'))
    body = db.Column(db.String(2048))
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow())

    author = db.relationship('User', backref='feedback')


class Invite(db.Model):
    __tablename__ = 'invite'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True)
    key = db.Column(db.String(8), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow())

    user = db.relationship('User', backref='invite')

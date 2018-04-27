from app import db, login

import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class User(UserMixin, db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    user_type = db.Column(db.Integer, index=True)
    full_name = db.Column(db.String(64), index=True)
    join_date = db.Column(db.DateTime, index=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow())

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class NewsItem(db.Model):
    __tablename__ = 'newsitem'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    title = db.Column(db.String(64), index=True)
    body = db.Column(db.String(2048), index=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow())

    acknowledgements = db.relationship('NewsItemAck', backref='acknowledger', lazy='dynamic')

    def get_acknowledgements(self, newsitem_id):
        return self.acknowledgements.filter_by(newsitem_id=newsitem_id).all()

    def is_acknowledged(self, user_id):
        return self.acknowledgements.filter_by(user_id=user_id).count() > 0


class NewsItemAck(db.Model):
    __tablename__ = 'newsitem_ack'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    newsitem_id = db.Column(db.Integer, db.ForeignKey('newsitem.id'))
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow())

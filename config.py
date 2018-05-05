import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'mow'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'ecgvolunteer.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ADDRESS = '127.0.0.1:5000'  # Change me in production

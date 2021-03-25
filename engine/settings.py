from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from os import getenv

db_user = getenv('DB_USER')
db_pass = getenv('DB_PASSWORD')
db_host = getenv('DB_HOST')
db_name = getenv('DB_NAME')


class DevelopmentConfig():
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root@localhost/gpsns'
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///gpsns.db'
    # SQLALCHEMY_DATABASE_URI = = f'mysql+pymysql://{db_user}:{db_pass}@{db_host}/{db_name}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True

class Config(DevelopmentConfig):
    DEBUG = False
    SQLALCHEMY_ECHO = False

db = SQLAlchemy()
ma = Marshmallow()


def init_db(app):
    db.init_app(app)
    Migrate(app, db)
    db.app = app

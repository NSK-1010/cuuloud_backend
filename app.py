#!/usr/bin/env python3
from flask import Flask
from flask_session import Session
from engine import init_db
import os
import logging
from flask_socketio import SocketIO

async_mode = None

def create_app():

    app = Flask(__name__, static_folder='static', static_url_path='')

    #SECRET_KEY
    app.config['SECRET_KEY'] = os.urandom(24)

    #Flask Config
    app.config.from_object('engine.DevelopmentConfig')

    #sqlalchemy log setting
    logging.basicConfig()
    logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
    logging.getLogger('sqlalchemy.orm.unitofwork').setLevel(logging.DEBUG)

    #database.py
    init_db(app)

    return app

app = create_app()

Session(app)

socketio = SocketIO(app, async_mode=async_mode, manage_session=False)
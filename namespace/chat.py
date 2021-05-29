from flask_socketio import Namespace, emit, join_room, leave_room, close_room, rooms, disconnect
from util import randomstr, crypt, user
from engine import db
from model import Room, RoomSchema, Join, User, Invite
from app import app, session
from flask_session import Session
Session(app)
class ChatNameSpace(Namespace):
    def on_connect(self):
        print('connected(chat)')
        pass

    def on_disconnect(self):
        pass
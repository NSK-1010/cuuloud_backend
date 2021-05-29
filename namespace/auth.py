from flask_socketio import Namespace, emit, join_room, leave_room, close_room, rooms, disconnect
from util import randomstr, crypt, user
from engine import db
from model import Room, RoomSchema, Join, User, Invite
from app import app, session
from flask_session import Session
Session(app)
class AuthNameSpace(Namespace):
    def on_connect(self):
        print('connected(auth)')
        emit('login', {'login': session.get('login'), 'id': session.get('id')})

    def on_disconnect(self):
        pass
    
    def on_login(self, payload):
        print(payload)
        if session.get('login'):
            return
        session['login'] = False
        target = User.query.filter(User.id == payload.get('id')).first()
        if (not target) or (not crypt.check(payload.get('password'), target.password)):
            emit('error', {'message': 'This is wrong ID or password.'})
            return
        session['id'] = payload.get('id')
        session['login'] = True
        my_join_rooms = Join.query.filter(
            Join.user_id == session.get('id')).all()
        schema = RoomSchema(many=True)
        emit('login', {'login': session.get('login'), 'id': session.get('id')})
        emit('rooms', {'ids': schema.dump(my_join_rooms)})

    def on_logout(self):
        session['id'] = None
        session['login'] = False
        emit('login', {'login': session.get('login'), 'id': session.get('id')})

    def on_invite(self, payload):
        if not session.get('login'):
            emit('error', {'message': 'You need to log in.'})
            return
        target = Invite.query.filter(
            Invite.email == payload.get('email')).first()
        if target:
            emit('notice', {'message': 'This email has already invited.'})
            return
        email = payload.get("email")
        new = Invite(user_id=session.get('id'), email=email)
        db.session.add(new)
        db.session.commit()
        emit('invited', {'email': email})

    def on_register(self, payload):
        if not payload.get('id').isascii():
            return
        target = User.query.filter(User.id == payload.get('id')).first()
        if target:
            emit('notice', {'message': 'This ID has already found.'})
            return
        del target
        name = payload.get("name")
        email = payload.get("email")
        password = crypt.hash(payload.get("password"))
        target = Invite.query.filter(Invite.email == email).first()
        if not target:
            emit('notice', {'message': 'You are not invited.'})
            return
        new = User(name=name, email=email, password=password)
        db.session.add(new)
        session['id'] = payload.get('id')
        session['login'] = True
        emit('registed', {'id': session['id']})
        db.session.commit()

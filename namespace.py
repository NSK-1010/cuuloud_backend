from flask import session
from flask_socketio import Namespace, emit, join_room, leave_room, close_room, rooms, disconnect
from util import randomstr, crypt
from engine import db
from model import Room, Join, User, Invite

class Namespace(Namespace):
    def on_connect(self):
        if session.get('id'):
            emit('status', {'message':f'You are logged in to {session.get("id")}.'})
        else:
            emit('status', {'message':f'You need to log in.'})


    def on_disconnect(self):
        my_join = Join.query(Join.user_id == session.get('id')).first()
        if not my_join:
            return
        db.session.delete(my_join)
        leave_room(my_join.room_id)
        emit('status', {'message':f'{session.get("id")} has disconnected.'}, room=my_join.room_id)
        db.session.commit()
    
    def on_create_room(self, payload):
        if not session.get('id'):
            emit('status', {'message':'You need to log in.'})
            return
        name = payload.get('name')
        room = randomstr.randomstr(20)
        while Room.query(Room.id == room).first():room = randomstr.randomstr(20)
        new_room = Room(id=room, name=name)
        new_join = Join(user_id=session.get('id'),room_id=room)
        db.session.add(new_room)
        db.session.add(new_join)
        join_room(room)
        db.session.commit()
        emit('status', {'message':f'{name} was created.'}, room=room)
    
    def on_join_room(self, payload):
        if not session.get('login'):
            emit('status', {'message':'You need to log in.'})
            return
        room = payload.get('room')
        target = Room.query(Room.id == room).first()
        if not target:
            emit('error', {'message':'That room is not found.'})
            return
        new_join = Join(user_id=session.get('id'),room_id=room)
        db.session.add(new_join)
        join_room(room)
        emit('status', {'message':f'You are joined in {target.name}.'})
        emit('status', {'message':f'{session.get("id")} has joined.'}, room=room)
        db.session.commit()
            
    def on_leave_room(self, payload):
        if not session.get('login'):
            emit('status', {'message':'You need to log in.'})
            return
        room = payload.get('room')
        my_join = Join.query(Join.user_id == session.get('id'), Join.room_id == room).first()
        if not my_join:
            emit('error', {'message':'You are not joined.'})
            return
        db.session.delete(my_join)
        leave_room(room)
        emit('status', {'message':f'{session.get("id")} has left.'}, room=room)
        db.session.commit()
        
    def on_login(self, payload):
        target = User.query.filter(User.id == payload.get('id')).first()
        if (not target) or (not crypt.check(payload.get('password'), target.password)):
            emit('error', {'message':'This is wrong ID or password.'})
            return
        session['id'] = payload.get('id')
        session['login'] = True

    def on_invite(self, payload):
        if not session.get('login'):
            emit('status', {'message':'You need to log in.'})
            return
        if payload.get('id').isascii():
            return
        target = Invite.query.filter(Invite.email == payload.get('email')).first()
        if target:
            emit('error', {'message':'This email has already invited.'})
            return
        email = payload.get("email")
        new = Invite(user_id=session.get('id'), email=email)
        db.session.add(new)
        emit('status', {'message':'You are registed!'})
        db.session.commit()

    def on_register(self, payload):
        if payload.get('id').isascii():
            return
        target = User.query.filter(User.id == payload.get('id')).first()
        if target:
            emit('error', {'message':'This ID has already found.'})
            return
        del target
        name = payload.get("name")
        email = payload.get("email")
        password = crypt.hash(payload.get("password"))
        target = Invite.query.filter(Invite.email == email).first()
        if not target:
            emit('error', {'message':'You are not invited.'})
            return
        new = User(name=name, email=email, password=password)
        db.session.add(new)
        session['id'] = payload.get('id')
        session['login'] = True
        emit('status', {'message':'You are registed!'})
        db.session.commit()

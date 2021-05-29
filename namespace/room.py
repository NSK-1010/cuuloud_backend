from flask_socketio import Namespace, emit, join_room, leave_room, close_room, rooms, disconnect
from util import randomstr, crypt, user
from engine import db
from model import Room, RoomSchema, Join, User, Invite
from app import app, session
from flask_session import Session
Session(app)

class RoomNameSpace(Namespace):
    def on_connect(self):
        print('connected(room)')
        my_join_data = Join.query.filter(
            Join.user_id == session.get('id')).all()
        for r in my_join_data:
            join_room(r.room_id)
        room_schema = RoomSchema(many=False)
        my_join_rooms = [room_schema.dump(Room.query.filter(Room.id == r.room_id).first()) for r in my_join_data]
        emit('joinned_rooms', my_join_rooms)
        room_schema = RoomSchema(many=True)
        emit('rooms', room_schema.dump(Room.query.all()))

    def on_disconnect(self):
        my_join = Join.query.filter(Join.user_id == session.get('id')).all()
        if not my_join:
            return
        for join in my_join:
            leave_room(join.room_id)
            emit('leaving', {'id': session.get("id"), 'room':join.room_id}, room=join.room_id)

    def on_create_room(self, payload):
        if not session.get('id'):
            emit('error', {'message': 'You need to log in.'})
            return
        name = payload.get('name')
        room = randomstr.randomstr(20)
        while Room.query.filter(Room.id == room).first():
            room = randomstr.randomstr(20)
        new_room = Room(id=room, name=name)
        new_join = Join(user_id=session.get('id'), room_id=room)
        db.session.add(new_room)
        db.session.add(new_join)
        db.session.commit()
        join_room(room)
        emit('join', {'id': session.get('id'), 'room': room}, room=room)
        my_join_rooms = Join.query.filter(
            Join.user_id == session.get('id'), Join.room_id == room).all()
        room_schema = RoomSchema(many=True)
        emit('joinned_rooms', {'rooms': room_schema.dump(my_join_rooms)})

    def on_join_room(self, payload):
        if not session.get('login'):
            emit('status', {'error': 'You need to log in.'})
            return
        room = payload.get('room')
        target = Room.query.filter(Room.id == room).first()
        if not target:
            emit('error', {'error': 'That room is not found.'})
            return
        my_join = Join.query.filter(Join.user_id == session.get('id'), Join.room_id == room).first()
        if my_join:
            return
        new_join = Join(user_id=session.get('id'), room_id=room)
        db.session.add(new_join)
        join_room(room)
        emit('join', {'room': room, 'id': session.get("id")}, room=room)
        db.session.commit()
        my_join_rooms = Join.query(
            Join.user_id == session.get('id'), Join.room_id == room).all
        schema = RoomSchema(many=True)
        emit('joinned_rooms', {'ids': schema.dump(my_join_rooms)})

    def on_leave_room(self, payload):
        if not session.get('login'):
            emit('error', {'message': 'You need to log in.'})
            return
        room = payload.get('room')
        my_join = Join.query(Join.user_id == session.get(
            'id'), Join.room_id == room).first()
        if not my_join:
            emit('error', {'message': 'You are not joined.'})
            return
        db.session.delete(my_join)
        leave_room(room)
        emit('leave', {'room': room, 'id': session.get("id")}, room=room)
        db.session.commit()
        my_join_rooms = Join.query(
            Join.user_id == session.get('id'), Join.room_id == room).all
        schema = RoomSchema(many=True)
        emit('joinned_rooms', {'rooms': schema.dump(my_join_rooms)})

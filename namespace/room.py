from flask_socketio import Namespace, emit, join_room, leave_room, close_room, rooms, disconnect
from util import randomstr, crypt
from config import conf
from engine import db
from model import Room, RoomSchema, Join, User, Invite
from app import app, session
from flask_session import Session
import datetime
Session(app)


class RoomNameSpace(Namespace):
    def on_connect(self):
        print('connected(room)')
        my_join_data = Join.query.filter(
            Join.user_id == session.get('id')).all()
        for r in my_join_data:
            join_room(r.room_id)
        room_schema = RoomSchema(many=False)
        my_join_rooms = [room_schema.dump(Room.query.filter(
            Room.id == r.room_id).first()) for r in my_join_data]
        emit('joinned_rooms', my_join_rooms)
        if session.get('login'):
            room_schema = RoomSchema(many=True)
            emit('rooms', room_schema.dump(Room.query.all()))

    def on_disconnect(self):
        my_join = Join.query.filter(Join.user_id == session.get('id')).all()
        if not my_join:
            return
        for join in my_join:
            leave_room(join.room_id)

    def on_get_all_rooms(self):
        if not session.get('login'):
            emit('notice', {'message': 'ログインが必要です'})
            return
        room_schema = RoomSchema(many=True)
        emit('rooms', room_schema.dump(Room.query.all()))
        my_join_data = Join.query.filter(
            Join.user_id == session.get('id')).all()
        for r in my_join_data:
            join_room(r.room_id)
        room_schema = RoomSchema(many=False)
        my_join_rooms = [room_schema.dump(Room.query.filter(
            Room.id == r.room_id).first()) for r in my_join_data]
        emit('joinned_rooms', my_join_rooms)

    def on_create_room(self, payload):
        if not session.get('login'):
            emit('notice', {'message': 'ログインが必要です。'})
            return
        if not payload.get('name').split():
            emit('notice', {'message': '部屋の名前を入力してください。'})
            return
        before_created = Room.query.filter(
            Room.host_id == session.get('id')).first()
        if before_created:
            limit = datetime.timedelta(
                minutes=conf.app.get('lim_min_createroom'))
            if datetime.datetime.now() - before_created.created_at < limit:
                emit('notice', {
                     'message': f'''一度にたくさんの部屋は作れません。
                     あと{round(((limit - (datetime.datetime.now() - before_created.created_at)).seconds)/60)}分ほどお待ちください。'''})
                return
            else:
                del limit, before_created
        room = randomstr.randomstr(20)
        while Room.query.filter(Room.id == room).first():
            room = randomstr.randomstr(20)
        me = User.query.filter(User.id == session.get('id')).first()
        new_room = Room(id=room, name=payload.get('name'),
                        host_id=session.get('id'), host_name=me.name)
        new_join = Join(user_id=session.get('id'), room_id=room)
        db.session.add(new_room)
        db.session.add(new_join)
        db.session.commit()
        join_room(room)
        emit('join', {'user_id': session.get('id'), 'text': None, 'user_name': me.name,
             'created_at': datetime.datetime.now().isoformat(), 'room_id': room}, room=room)
        my_join_data = Join.query.filter(
            Join.user_id == session.get('id')).all()
        room_schema = RoomSchema(many=False)
        my_join_rooms = [room_schema.dump(Room.query.filter(
            Room.id == r.room_id).first()) for r in my_join_data]
        emit('joinned_rooms', my_join_rooms)
        room_schema = RoomSchema(many=True)
        emit('rooms', room_schema.dump(Room.query.all()), broadcast=True)

    def on_join_room(self, payload):
        if not session.get('login'):
            emit('notice', {'message': 'ログインが必要です。'})
            return
        room = payload.get('room')
        target = Room.query.filter(Room.id == room).first()
        if not target:
            emit('notice', {'message': 'この部屋は存在しません。'})
            room_schema = RoomSchema(many=True)
            emit('rooms', room_schema.dump(Room.query.all()), broadcast=True)
            return
        my_join = Join.query.filter(Join.user_id == session.get(
            'id'), Join.room_id == room).first()
        if my_join:
            return
        new_join = Join(user_id=session.get('id'), room_id=room)
        db.session.add(new_join)
        join_room(room)
        db.session.commit()
        my_join_data = Join.query.filter(
            Join.user_id == session.get('id')).all()
        room_schema = RoomSchema(many=False)
        my_join_rooms = [room_schema.dump(Room.query.filter(
            Room.id == r.room_id).first()) for r in my_join_data]
        emit('joinned_rooms', my_join_rooms)
        emit('join', {'room_id': room, 'created_at': datetime.datetime.now().isoformat(), 'text': None, 'user_id': session.get('id'), 'user_name': User.query.filter(
            User.id == session.get('id')).first().name}, room=room)

    def on_leave_room(self, payload):
        if not session.get('login'):
            emit('notice', {'message': 'ログインが必要です。'})
            return
        room = payload.get('room')
        my_join = Join.query.filter(Join.user_id == session.get(
            'id'), Join.room_id == room).first()
        if not my_join:
            emit('notice', {'message': 'この部屋に参加してません。'})
            return
        db.session.delete(my_join)
        leave_room(room)
        emit('leave', {'room_id': room, 'created_at': datetime.datetime.now().isoformat(), 'text': None, 'user_id': session.get('id'), 'user_name': User.query.filter(
            User.id == session.get('id')).first().name}, room=room)
        db.session.commit()
        my_join_data = Join.query.filter(
            Join.user_id == session.get('id')).all()
        room_schema = RoomSchema(many=False)
        my_join_rooms = [room_schema.dump(Room.query.filter(
            Room.id == r.room_id).first()) for r in my_join_data]
        emit('joinned_rooms', my_join_rooms)
        joinned_member = Join.query.filter(Join.room_id == room).first()
        if not joinned_member:
            db.session.delete(Room.query.filter(Room.id == room).first())
            db.session.commit()
            room_schema = RoomSchema(many=True)
            emit('rooms', room_schema.dump(Room.query.all()), broadcast=True)

    def on_message(self, payload):
        if not payload.get('text').split():
            emit('notice', {'message': '発言を入力してください。'})
            return
        emit('message', {'text': payload.get('text'), 'room_id': payload.get(
            "id"), 'created_at': datetime.datetime.now().isoformat(), 'user_id': session.get('id'), 'user_name': User.query.filter(User.id == session.get('id')).first().name}, room=payload.get('id'))

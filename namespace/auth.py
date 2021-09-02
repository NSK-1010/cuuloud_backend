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
        target = User.query.filter(User.id == session.get('id')).first()
        emit('login', {'login': session.get('login'), 'id': session.get('id'), 'name':target.name})

    def on_disconnect(self):
        pass
    
    def on_login(self, payload):
        if session.get('login'):
            return
        session['login'] = False
        target = User.query.filter(User.id == payload.get('id')).first()
        if (not target) or (not crypt.check(payload.get('password'), target.password)):
            emit('error', {'message': 'IDかパスワードが間違っています。'})
            return
        session['id'] = payload.get('id')
        session['login'] = True
        my_join_rooms = Join.query.filter(
            Join.user_id == session.get('id')).all()
        schema = RoomSchema(many=True)
        emit('login', {'login': session.get('login'), 'id': session.get('id'), 'name':target.name})
        emit('rooms', {'ids': schema.dump(my_join_rooms)})

    def on_logout(self):
        session['id'] = None
        session['login'] = False
        emit('login', {'login': session.get('login'), 'id': session.get('id')})

    def on_invite(self, payload):
        if not session.get('login'):
            emit('error', {'message': 'ログインが必要です。'})
            return
        target = Invite.query.filter(
            Invite.email == payload.get('email')).first()
        if target:
            emit('notice', {'message': 'このメールアドレスはすでに招待されています。'})
            return
        email = payload.get("email")
        if email.count('@') != 1 or email.split('@')[-1].count('.') == 0:
            emit('notice', {'message': '不正なメールアドレスです。'})
            return
        new = Invite(user_id=session.get('id'), email=email)
        db.session.add(new)
        db.session.commit()
        emit('notice', {'message': '招待が完了しました。'})

    def on_register(self, payload):
        if not payload.get('id').isascii():
            return
        target = User.query.filter(User.id == payload.get('id')).first()
        if target:
            emit('notice', {'message': '登録しようとしているIDがすでに存在します。'})
            return
        del target
        name = payload.get("name")
        email = payload.get("email")
        password = crypt.hash(payload.get("password"))
        target = Invite.query.filter(Invite.email == email).first()
        if not target:
            emit('notice', {'message': 'あなたは招待されていません。'})
            return
        new = User(id=payload.get('id'), name=name, email=email, password=password)
        db.session.add(new)
        session['id'] = payload.get('id')
        session['login'] = True
        emit('registed', {'id': session['id']})
        db.session.commit()

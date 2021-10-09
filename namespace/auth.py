from flask_socketio import Namespace, emit, join_room, leave_room, close_room, rooms, disconnect
from util import randomstr, crypt, mail, url
from engine import db
from model import RoomSchema, Join, User, Invite, Verify, verify
from app import app, session
from flask_session import Session
Session(app)


class AuthNameSpace(Namespace):
    def on_connect(self):
        print('connected(auth)')
        if session.get('verify'):
            verify = Verify.query.filter(
                Verify.token == session.get('verify')).first()
            if verify:
                verified_user = User.query.filter(
                    User.id == verify.user_id).first()
                emit('notice', {
                     'message': 'メールアドレス認証が成功しました！ログインをして、サービスをお楽しみください！'})
                verified_user.verified = True
                db.session.delete(verify)
                db.session.commit()
                emit('login', {'login': False, 'id': None, 'name': None})
                session['verify'] = None
        if session.get('login'):
            target = User.query.filter(User.id == session.get('id')).first()
            target.ip = str(session.get('ip'))
            db.session.commit()
            emit('login', {'login': session.get('login'),
                 'id': session.get('id'), 'name': target.name})
        else:
            emit('login', {'login': False, 'id': None, 'name': None})

    def on_disconnect(self):
        pass

    def on_login(self, payload):
        if session.get('login'):
            return
        session['login'] = False
        target = User.query.filter(User.id == payload.get('id')).first()
        if (not target) or (not crypt.check(payload.get('password'), target.password)):
            emit('auth_error', {'message': 'IDかパスワードが間違っています。'})
            return
        target.ip = str(session.get('ip'))
        db.session.commit()
        if not target.verified:
            emit('auth_error', {'message': 'メールアドレス認証が済まされていません。'})
            return
        session['id'] = payload.get('id')
        session['login'] = True
        my_join_rooms = Join.query.filter(
            Join.user_id == session.get('id')).all()
        schema = RoomSchema(many=True)
        emit('login', {'login': session.get('login'),
             'id': session.get('id'), 'name': target.name})
        emit('rooms', {'ids': schema.dump(my_join_rooms)})

    def on_logout(self):
        session['id'] = None
        session['login'] = False
        emit('login', {'login': session.get('login'), 'id': session.get('id')})

    def on_apply_settings(self, payload):
        if not session.get('login'):
            emit('notice', {'message': 'ログインが必要です。'})
            return
        me = User.query.filter(User.id == session.get('id')).first()
        if payload.get('changedName') and payload.get('name').split():
            me.name = payload.get('name')
            db.session.commit()
        emit('changed_settings', {'name': me.name})
        emit('notice', {'message': '設定を適用しました。'})

    def on_invite(self, payload):
        if not session.get('login'):
            emit('notice', {'message': 'ログインが必要です。'})
            return
        if User.query.filter(User.email == payload.get("email")).first():
            emit('notice', {'message': 'このメールアドレスはすでに登録されています。'})
            return
        if Invite.query.filter(Invite.email == payload.get('email')).first():
            emit('notice', {'message': 'このメールアドレスはすでに招待されています。'})
            return
        email = payload.get("email") if payload.get("email") else ''
        if not (email.count('@') == 1 and email.split('@')[-1].count('.') != 0):
            emit('notice', {'message': '不正なメールアドレスです。'})
            return
        invited_person = User.query.filter(
            User.id == session.get('id')).first()
        if invited_person.invitation_times_limit <= 0:
            emit('notice', {'message': '招待可能回数を超過しました。'})
            return
        invited_person.invitation_times_limit -= 1
        new = Invite(user_id=session.get('id'), email=email)
        db.session.add(new)
        db.session.commit()
        me = User.query.filter(User.id == session.get('id')).first()
        mail.send_template(payload.get(
            'email'), f'{me.name}からCuuloudへの招待が届きました！', 'invite', url=url.url, name=me.name)
        emit('notice', {'message': '招待が完了しました。'})

    def on_register(self, payload):
        if not payload.get('id').isascii():
            emit('auth_error', {'message': 'IDにはASCII文字しか使えません。'})
            return
        if User.query.filter(User.id == payload.get('id')).first():
            emit('auth_error', {'message': '登録しようとしているIDがすでに存在します。'})
            return
        if User.query.filter(User.email == payload.get("email")).first():
            emit('auth_error', {'message': 'このメールアドレスはすでに登録されています。'})
            return
        target = Invite.query.filter(
            Invite.email == payload.get("email")).first()
        if not target:
            emit('auth_error', {'message': 'あなたは招待されていません。'})
            return
        if len(payload.get('name')) > 10:
            emit('auth_error', {'message': '名前が長すぎます。'})
            return
        if len(payload.get('id')) > 15:
            emit('auth_error', {'message': 'IDが長すぎます。'})
            return
        password = crypt.hash(payload.get("password"))
        new = User(id=payload.get('id'), name=payload.get("name"),
                   email=payload.get("email"), password=password, verified=False)
        verify_token = randomstr.randomstr(10)
        while Verify.query.filter(Verify.token == verify).first():
            verify_token = randomstr.randomstr(10)
        new_verify = Verify(token=verify_token, user_id=payload.get('id'))
        db.session.delete(target)
        db.session.add(new)
        db.session.add(new_verify)
        session['id'] = payload.get('id')
        db.session.commit()
        emit('auth_error', {'message': '登録されたメールアドレスから認証してください。'})
        mail.send_template(payload.get('email'), 'Cuuloud　メール認証の確認',
                           'register', url=url.url, verify_token=verify_token)

def islogin(session):
    return 'login' in session and session['login']


def user_alias(id: str, session):
    if id == 'me':
        if islogin(session):
            return session["user"]
        else:
            return None
    elif id.isascii():
        return id
    else:
        return None


def getname(id: str):
    from ..model import User
    target = User.query.filter(User.id == payload.get('id')).first()
    return target.name if target else None

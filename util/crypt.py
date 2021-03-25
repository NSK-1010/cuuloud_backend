import bcrypt


def hash(password: str):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=16)).decode()


def check(password: str, hashed_password: str):
    return bcrypt.checkpw(password.encode(), hashed_password.encode())

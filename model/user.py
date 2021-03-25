from engine.settings import db, ma
from datetime import datetime


class User(db.Model):
    id = db.Column(db.String(length=255), primary_key=True, unique=True)
    password = db.Column(db.String(length=255))
    name = db.Column(db.Unicode(length=255))
    email = db.Column(db.Unicode(length=255))
    
    invitation_times_limit = db.Column(db.Integer)
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.now)

    __tablename__ = 'user'


class UserSchema(ma.Schema):
    class Meta:
        fields = ("id", "name", "created_at")

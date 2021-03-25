from app import app, socketio
from threading import Lock
from flask_socketio import emit, join_room, leave_room, close_room, rooms, disconnect

thread = None
thread_lock = Lock()

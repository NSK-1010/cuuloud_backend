from flask import render_template, send_file
from app import app, socketio
from namespace import *

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/favicon.ico')
def favicon():
    return send_file('../dist/favicon.ico')

socketio.on_namespace(auth.AuthNameSpace('/auth'))
socketio.on_namespace(room.RoomNameSpace('/room'))
socketio.on_namespace(chat.ChatNameSpace('/chat'))
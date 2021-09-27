from flask import render_template, send_file, redirect, url_for
from app import app, socketio, session
from namespace import *
from flask_session import Session
Session(app)
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/verify/<id>')
def verify(id):
    session['verify'] = id
    return redirect(url_for('index'))

@app.route('/favicon.ico')
def favicon():
    return send_file('../dist/favicon.png')

socketio.on_namespace(auth.AuthNameSpace('/auth'))
socketio.on_namespace(room.RoomNameSpace('/room'))
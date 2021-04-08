from flask import Flask, render_template, redirect, url_for, session, request
from flask_socketio import SocketIO, join_room, leave_room, send, emit
from secrets import secret_key
from datetime import datetime
from forms import *
import urllib.parse
from functions import *
from models import *
from words import return_words_string

# app config
app = Flask(__name__)
app.secret_key = secret_key

# SocketIO config
socketio = SocketIO(app)

# db config
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///kalamburyDB.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# server routes
# home route
@app.route("/", methods=['GET', 'POST'])
def index():
    index_form = IndexForm()
    if index_form.validate_on_submit():
        if index_form.submitJoin.data:
            username = index_form.username.data
            session['username'] = username
            return redirect(url_for('join_existing_room'))
        if index_form.submitCreate.data:
            username = index_form.username.data
            session['username'] = username
            return redirect(url_for('create_room'))
    return render_template("index.html", form=index_form)


# createRoom route
@app.route("/createRoom", methods=['GET', 'POST'])
def create_room():
    if 'username' not in session:
        return redirect(url_for('index'))
    create_form = CreateRoomForm()
    room_id = generate_room_id()
    session['room_id'] = room_id
    if create_form.validate_on_submit():
        turn_length = request.form["turn_length"]
        turn_count = request.form["turn_count"]

        words = return_words_string()
        words_array = words.split(';')
        room = Room(room_id=session['room_id'], admin_username=session["username"], current_word=words_array[0], words=words, who_draws=session["username"], turn_count=turn_count, turn_length=turn_length)
        db.session.add(room)
        db.session.commit()

        return redirect(url_for('game'))
    return render_template("createRoom.html", form=create_form)


# joinRoom route
@app.route("/joinRoom", methods=['GET', 'POST'])
def join_existing_room():
    if 'username' not in session:
        return redirect(url_for('index'))
    join_form = JoinRoomForm()
    if join_form.validate_on_submit():
        session['room_id'] = join_form.room_id.data
        return redirect(url_for('game'))
    return render_template("joinRoom.html", form=join_form)


# game route
@app.route("/game", methods=['GET', 'POST'])
def game():
    if 'room_id' not in session:
        return redirect(url_for('index'))

    return render_template("game.html", room_id=session['room_id'])


# join route
@app.route('/join/<room_id>', methods=['GET', 'POST'])
def join(room_id):
    # delete actual room_pass_string
    if 'room_id' in session:
        session.pop('room_id', None)
    session['room_id'] = room_id
    return redirect(url_for('game'))


# exit route
# used for delete room_pass_string from session
@app.route("/exit", methods=['GET', 'POST'])
def Exit():
    session.pop('room_id', None)
    return redirect(url_for('index'))


# background processes
@app.route('/start_game')
def start_game():
    print("Gra sie zaczela")
    return ""


# socketIO functions
@socketio.on('message')
def on_message(received_data):
    username = session['username']
    room = session['room_id']
    time = str(datetime.now().hour) + ":" + str(datetime.now().minute) + ":" + str(datetime.now().second)

    word = return_current_word(room)
    if urllib.parse.unquote(received_data['message_data']) == word:
        # zmien hasla w bazie
        # dodaj punkty graczowi
        # + cala inna logika ktora trzeba zrobic
        change_current_word(room)
        emit('correct', {"word": word, 'username': username}, room=room)
    send({'message_data': received_data['message_data'], 'username': username, 'time': time}, room=room)


@socketio.on('join')
def on_join(received_data):
    username = session['username']
    room = session['room_id']
    join_room(room)
    add_user_to_db(username, room)
    send({'alert': username + ' dołączył do pokoju.'}, room=room)


@socketio.on('leave')
def on_leave(received_data):
    username = session['username']
    room = session['room_id']
    leave_room(room)
    session.pop('room_id', None)
    delete_user_from_db(username, room)
    send({'alert': username + ' opuścił pokój.'}, room=room)


@socketio.on('draw')
def on_draw(received_data):
    room = session['room_id']
    emit('draw', received_data, room=room)


# run app
if __name__ == '__main__':
    socketio.run(app, debug=True)

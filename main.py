from flask import Flask, render_template, redirect, url_for, session, request,jsonify
from flask_socketio import SocketIO, join_room, leave_room, send, emit
from secrets import secret_key
from datetime import datetime
from forms import *
import urllib.parse
from functions import *
from models import *
from words import get_words_string

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
        try:
            words = get_words_string(int(turn_count))
            room = Room(room_id=session['room_id'], admin_username=session["username"], current_word="", words=words, who_draws=session["username"], turn_count=turn_count, turn_length=turn_length, game_state="game_ready")
            db.session.add(room)
            db.session.commit()
            return redirect(url_for('game'))
        except ValueError:
             return redirect(url_for('error', error_type="error"))

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


# error route
@app.route("/error/<error_type>", methods=['GET', 'POST'])
def error(error_type):
    return render_template("error.html", error_type=error_type)



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


### background processes

# click on the start button
@app.route('/start_game')
def start_game():
    room = session['room_id']
    if check_game_state(room) == "game_ready":
        username = request.args.get('username', 0, type=str)
        if return_admin_username(room) == username:
            prepare_round_for_room(room)
    return jsonify(word="...")


# route which is used by user who draws to get the word
@app.route('/get_word')
def get_word():
    room = request.args.get('room_id', 0, type=str)
    return jsonify(word=return_current_word(room))


# socketIO functions
@socketio.on('message')
def on_message(received_data):
    username = session['username']
    room = session['room_id']
    time = str(datetime.now().hour) + ":" + str(datetime.now().minute) + ":" + str(datetime.now().second)

    original_word = return_current_word(room)
    word = clear_string(original_word)
    guess = clear_string(urllib.parse.unquote(received_data['message_data']))

    if username == return_drawer_username(room) and  check_game_state(room) != "game_ready":
        return
    if guess == word: # and game_state != "game_paused": 
        # zmien hasla w bazie
        change_users_score(username, room)
        change_game_state(room,'ready_to_next_round')
        # change_drawer_score(username, room) 
        emit('correct', {"word": original_word, 'username': username}, room=room)

        # change drawer and start game
        prepare_round_for_room(room)
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
    if username == return_admin_username(room):
        kick_all_players_from_room(room, username)
    else:
        leave_room(room)
        session.pop('room_id', None)
        delete_user_from_db(username, room)
        send({'alert': username + ' opuścił pokój.'}, room=room)


@socketio.on('draw')
def on_draw(received_data):
    room = session['room_id']
    username = session['username']
    if username != return_drawer_username(room):
        return
    emit('draw', received_data, room=room)

@socketio.on('clear')
def clean(received_data):
    room = session['room_id']
    emit('clear', received_data, room=room)

@socketio.on('time_end')
def time_end(received_data):
    room = received_data["room"]
    sender = received_data["sender"]
    if check_game_state(room) != "ready_to_next_round" and sender == return_admin_username(room):
        emit('time_is_over',  {"word": return_current_word(room)}, room=room)
        prepare_round_for_room(room)


@socketio.on('end_game')
def end_game(received_data):
    room = received_data["room"]
    sender = received_data["sender"]
    emit('stop_game',  {"winner": return_admin_username(room)}, room=room)

    
@socketio.on('hint')
def hint(received_data):
    room = received_data["room"]
    letters = received_data["letters"]
    emit('show_hint', {"hint": return_hint(room, letters)}, room=room)

def prepare_round_for_room(room):

    change_drawer(room)

    change_current_word(room)

    # start timer
    turn_length = get_turn_length(room)
    socketio.emit('start_timer', {"time": turn_length}, room=room)

    # change game state
    change_game_state(room,'game_in_progress')

    # send emit to the user who draws this round
    socketio.emit('who_draws', {"username": return_drawer_username(room)}, room=room)

    # clear canvas
    socketio.emit('clear', "", room=room)


def kick_all_players_from_room(room, username):
    room_from_db = Room.query.filter_by(room_id=room).first()
    if room_from_db:
        socketio.emit('kick_all',{"admin": username}, room=room)
        delete_room(room)
        delete_users(room)


# run app
if __name__ == '__main__':
    socketio.run(app, debug=True)
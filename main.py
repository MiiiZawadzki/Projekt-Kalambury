import os
from flask import Flask, render_template, redirect, url_for, session, request,jsonify
from flask_socketio import SocketIO, join_room, leave_room, send, emit
from secret_key import key
from datetime import datetime
from forms import *
import urllib.parse
from functions import *
from models import *
from words import get_words_string
import ast
from engineio.payload import Payload
from time import sleep

Payload.max_decode_packets = 500
# app config
app = Flask(__name__)
app.secret_key = key

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
        file = open("static/canvasIMG/{}.txt".format(room_id), "w")
        file.close()
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

@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template("error.html", error_type="Nie ma takiej strony")

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
    return ""


# route which is used by user who draws to get the word
@app.route('/get_word')
def get_word():
    room = request.args.get('room_id', 0, type=str)
    return jsonify(word=return_current_word(room))

@app.route('/skip_round')
def skip_round():
    room = request.args.get('room_id', 0, type=str)
    username = request.args.get('username', 0, type=str)
    if check_game_state(room) == "game_in_progress" and username == return_drawer_username(room):
        decrease_user_points(username, room)
        socketio.emit('skip', {"username": username}, room=room)
        prepare_round_for_room(room)
    return ""

@app.route('/set_timer')
def set_timer():
    room = request.args.get('room_id', 0, type=str)
    username = request.args.get('username', 0, type=str)
    return jsonify(time=return_time(room))

@app.route('/load_data_about_room')
def load_data_about_room():
    room = request.args.get('room_id', 0, type=str)
    if check_game_state(room) != "game_in_progress":
        return jsonify(drawer_username="---")
    return jsonify(drawer_username=return_drawer_username(room))

# socketIO functions
@socketio.on('message')
def on_message(received_data):
    username = session['username']
    room = session['room_id']
    time = str(datetime.now().hour) + ":" + str(datetime.now().minute) + ":" + str(datetime.now().second)

    if username == return_drawer_username(room) and check_game_state(room) == "game_in_progress":
        return

    send({'message_data': received_data['message_data'], 'username': username, 'time': time}, room=room)

    original_word = return_current_word(room)
    word = clear_string(original_word)
    word_bez_pl = delete_diacritics(word)
    word_bez_pl = word_bez_pl.split()
    guess = urllib.parse.unquote(received_data['message_data'])
    guess = clear_string(guess)
    guess = delete_diacritics(guess)
    guess = guess.split()

    if ''.join(guess) == ''.join(word_bez_pl) and check_game_state(room) == "game_in_progress":
        # zmien hasla w bazie
        change_users_score(username, room)
        change_game_state(room,'ready_to_next_round')
        # change_drawer_score(username, room) 
        emit('correct', {"word": original_word, 'username': username}, room=room)
        # change drawer and start game
        prepare_round_for_room(room)
    else:
        word = word.split()
        guessed = []
        for wurd in guess:
            if wurd in word_bez_pl:
                i = word_bez_pl.index(wurd)
                guessed.append(word[i])
        if len(guessed) == 1:
            send({'so_close': "Zmierzasz w dobrą stronę. Hasło zawiera słowo: " + guessed[0]}, room=room)
        elif len(guessed) > 1:
            send({'so_close': "Zmierzasz w dobrą stronę. Hasło zawiera słowa: " + ', '.join(guessed)}, room=room)


@socketio.on('join')
def on_join(received_data):
    username = session['username']
    room = session['room_id']
    user_list = get_users(room)
    join_room(room)
    add_user_to_db(username, room)
    send({'alert': username + ' dołączył do pokoju.'}, room=room)
    emit('table_update', {"table_data": get_users(room)}, room=room)

@socketio.on('leave')
def on_leave(received_data):
    username = session['username']
    room = session['room_id']
    user_list = get_users(room)
    emit('table_update', {"table_data": get_users(room)}, room=room)
    if username == return_admin_username(room):
        kick_all_players_from_room(room, username)
    else:
        if username == return_drawer_username(room):
            prepare_round_for_room(room)
            file = open("static/canvasIMG/{}.txt".format(room), "w")
            file.close()
            emit('clear', received_data, room=room)
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

    if check_game_state(room) != "game_in_progress":
        return

    try:
        file = open("static/canvasIMG/{}.txt".format(room), "a")
        file.write(str(received_data)+"\n")
        file.close()
    except:
        return redirect(url_for('error', error_type="error"))
    emit('draw', received_data, room=room)

@socketio.on('clear')
def clean(received_data):
    room = session['room_id']
    username = session['username']
    if username != return_drawer_username(room):
        return
    file = open("static/canvasIMG/{}.txt".format(room), "w")
    file.close()
    emit('clear', received_data, room=room)

@socketio.on('load')
def load(received_data):
    room = session['room_id']
    try:
        file = open("static/canvasIMG/{}.txt".format(room), "r")
        for line in file:
            data = ast.literal_eval(line.strip())
            sleep(0.01)
            emit('draw', data, room=room)
        file.close()
    except:
        return redirect(url_for('error', error_type="error"))


@socketio.on('time_end')
def time_end(received_data):
    room = received_data["room"]
    sender = received_data["sender"]
    if check_game_state(room) != "ready_to_next_round" and sender == return_admin_username(room):
        emit('time_is_over',  {"word": return_current_word(room)}, room=room)
        emit('clear', received_data, room=room)
        prepare_round_for_room(room)


@socketio.on('end_game')
def end_game(received_data):
    room = received_data["room"]
    sender = received_data["sender"]
    change_game_state(room, "game_ended")
    emit('stop_game',  {"winner": return_winner(room)}, room=room)


@socketio.on('timer_tick')
def timer_tick(received_data):
    room = received_data["room"]
    sender = received_data["sender"]
    time = received_data["time"]
    if sender == return_admin_username(room):
        set_timer_in_db(room, time)
        emit('single_tick',  {"time": return_time(room)}, room=room)

        turn_length = get_turn_length(room)
        if (turn_length > 30 and time == int(turn_length*0.5)) or (turn_length <= 30 and time == 15):
            send({'so_close': return_hint(room, 1)}, room=room)
        elif (turn_length > 40 and time == int(turn_length*0.25)) or (turn_length <= 40 and time == 10):
            send({'so_close': return_hint(room, 2)}, room=room)
        elif (turn_length > 50 and time == int(turn_length*0.1)) or (turn_length <= 50 and time == 5):
            send({'so_close': return_hint(room, 0)}, room=room)

def prepare_round_for_room(room):
    change_drawer(room)
    change_current_word(room)

    # start timer
    turn_length = get_turn_length(room)
    socketio.emit('start_timer', {"time": turn_length}, room=room)
    set_timer_in_db(room, turn_length)

    # change game state
    change_game_state(room,'game_in_progress')

    # send emit to the user who draws this round
    socketio.emit('who_draws', {"username": return_drawer_username(room)}, room=room)

    # clear canvas
    file = open("static/canvasIMG/{}.txt".format(room), "w")
    file.close()
    socketio.emit('clear', "", room=room)
    
    #table update
    socketio.emit('table_update', {"table_data": get_users(room)}, room=room)
    
    if return_current_word(room) != "Skończyły się":
        socketio.send({'alert': return_turn_info(room)}, room=room)


def kick_all_players_from_room(room, username):
    room_from_db = Room.query.filter_by(room_id=room).first()
    if room_from_db:
        socketio.emit('kick_all',{"admin": username}, room=room)
        delete_room(room)
        delete_users(room)


# run app
if __name__ == '__main__':
    socketio.run(app, debug=True)

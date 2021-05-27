from random import choice
from string import ascii_letters, digits
from models import Room, User
from models import db
from random import randint
import time
import os

def return_current_word(room):
    room_from_db = Room.query.filter_by(room_id=room).first()
    if room_from_db:
        return room_from_db.current_word
    return ""


def change_current_word(room):
    room_from_db = Room.query.filter_by(room_id=room).first()
    if room_from_db:
        curr_words = room_from_db.words
        if len(curr_words) != 0:
            words = curr_words.split(';')
            i = randint(0, len(words)-1)
            new = words[i]
            words.remove(new)
            room_from_db.current_word = new
            words_string = ';'.join(words)
            data = {'words': words_string}
            db.session.query(Room).filter_by(room_id=room).update(data)
        else:
            room_from_db.current_word = "Skończyły się"
        db.session.commit()


def add_to_drawing_queue(username, room):
    room_from_db = Room.query.filter_by(room_id=room).first()
    if room_from_db:
        curr_queue = room_from_db.drawing_queue
        queue = curr_queue.split(';')
        queue.append(username)
        queue_string = ';'.join(queue)
        data = {'drawing_queue': queue_string}
        db.session.query(Room).filter_by(room_id=room).update(data)
        db.session.commit()
        

def change_drawer(room):
    room_from_db = Room.query.filter_by(room_id=room).first()
    if room_from_db:
        users = room_from_db.users
        if users:
            curr_drawer = room_from_db.who_draws
            users_list = users.split(';')
            curr_drawer_index = users_list.index(curr_drawer)
            new_drawer = users_list[(curr_drawer_index + 1) % len(users_list)]
            room_from_db.who_draws = new_drawer
            db.session.commit()

def return_hint(room, how_many_letters):
    room_from_db = Room.query.filter_by(room_id=room).first()
    if room_from_db:
        word = room_from_db.current_word
        if how_many_letters == 0:
            i = word.find(' ')
            if i < 3:
                hint = 'Pierwsze wyrazy hasła to: ' + word[:word.find(' ', i + 1)]
            else:
                hint = 'Pierwszy wyraz hasła to: ' + word[:i]
        elif how_many_letters == 1:
            hint = 'Pierwsza litera hasła to: ' + word[:1]
        else:
            hint = word[:how_many_letters]
            hint = hint.replace(' ', '_')
            hint = 'Pierwsze litery hasła to: ' + hint
        return hint

def clear_string(string):
    string = string.lower()
    for char in ",.-":
        string = string.replace(char, '')
    return string

def delete_diacritics(string):  # usuwanie polskich znaków
    string = string.replace('ą', 'a')
    string = string.replace('ć', 'c')
    string = string.replace('ę', 'e')
    string = string.replace('ł', 'l')
    string = string.replace('ń', 'n')
    string = string.replace('ó', 'o')
    string = string.replace('ś', 's')
    string = string.replace('ź', 'z')
    string = string.replace('ż', 'z')
    return string

def return_turn_info(room):
    room_from_db = Room.query.filter_by(room_id=room).first()
    if room_from_db:
        turn_count = room_from_db.turn_count
        words = room_from_db.words
        if words == "":
            return "RUNDA " + str(turn_count) + " z " + str(turn_count)
        else:
            return "RUNDA " + str(turn_count - len(words.split(';'))) + " z " + str(turn_count)


def change_game_state(room, game_state):
    room_from_db = Room.query.filter_by(room_id=room).first()
    if room_from_db:
        room_from_db.game_state = game_state       
        db.session.commit() 


def generate_room_id():
    lettersAndDigits = ascii_letters + digits
    room_id = ''.join((choice(lettersAndDigits) for i in range(16)))
    room_from_db = Room.query.filter_by(room_id=room_id).first()
    # If room with generated room_id does not exist, create new room
    if room_from_db is None:
        return room_id
    # If room with generated room_id does exist, call function one more time
    else:
        generate_room_id()


def delete_user_from_db(username, room):
    # delete from rooms
    room_from_db = Room.query.filter_by(room_id=room).first()
    if room_from_db:
        users_list = room_from_db.users
        if username in users_list:
            users = users_list.split(';')
            users.remove(username)
            users_string = ';'.join(users)

            data = {'users': users_string}

            db.session.query(Room).filter_by(room_id=room).update(data)
            db.session.commit()
            # delete room if is empty
            if len(room_from_db.users) == 0:
                db.session.delete(room_from_db)
                db.session.commit()

    # delete from users
    user_from_db = User.query.filter_by(room_id=room, username=username).first()
    if user_from_db:
        db.session.delete(user_from_db)
        db.session.commit()


def add_user_to_db(username, room):
    # add to rooms
    room_from_db = Room.query.filter_by(room_id=room).first()
    if room_from_db:
        if room_from_db.users is None:
            data = {'users': username}
            db.session.query(Room).filter_by(room_id=room).update(data)
        else:
            users_list = room_from_db.users
            users_list+=";"+username
            data = {'users': users_list}
            db.session.query(Room).filter_by(room_id=room).update(data)
        db.session.commit()
    
    # add to users
    user = User(room_id=room, username=username, score=0)
    db.session.add(user)
    db.session.commit()


def change_users_score(username, room):
    user_from_db = User.query.filter_by(room_id=room, username=username).first()
    room_from_db = Room.query.filter_by(room_id=room).first()
    drawer_from_db = User.query.filter_by(room_id=room, username=room_from_db.who_draws).first()
    if room_from_db:
        if user_from_db:
            if drawer_from_db:
                user_from_db.score += 10
                drawer_from_db.score += 5
                db.session.commit()

def get_users(room):
    users_from_db = User.query.filter_by(room_id=room).order_by(User.score.desc()).all()
    if users_from_db:
        users = []
        for user in users_from_db:
            users.append([user.username, user.score])
        #print(users)
        return users

def return_winner(room):
    users = get_users(room)
    if users:
        top_score = -101
        winner = []
        for user in users:
            if user[1] >= top_score:
                top_score = user[1]
                winner.append(user[0])
            else:
                break
        if top_score < 0:
            winner_string = 'Wszyscy jesteście chujowi'
        elif len(winner) > 1:
            winner_string = 'Remis! ' + ', '.join(winner) + ' zdobyli tyle samo punktów.'
        else:
            winner_string = 'Wygrał/a ' + winner[0] + '!' 
        return winner_string
    
def decrease_user_points(username, room):
    user_from_db = User.query.filter_by(room_id=room, username=username).first()
    if user_from_db:
        user_from_db.score -= 5
        db.session.commit()
# def change_drawer_score(username, room):
#     user_from_db = User.query.filter_by(room_id=room, username=username).first()

#     drawer = Room.query.filter_by(who_draws=username)
#     if user_from_db.username==drawer.who_draws:
#         user_from_db.score +=5
#         db.session.commit()


# def timer_countdown(t, room): 
#     while t:
#         if not Room.query.filter_by(room_id=room).first():
#             break
#         emit('timer_count', {'time': t}, room=room)
#         print(t, end=" \r")
#         time.sleep(1)
#         t -= 1
#     print("KONIEC CZASU")


def get_turn_length(room):
    room_from_db = Room.query.filter_by(room_id=room).first()
    if room_from_db:
        return int(room_from_db.turn_length)


def game_in_room_started(room):
    room_from_db = Room.query.filter_by(room_id=room).first()
    if room_from_db:
        return room_from_db.current_word != ""


def check_game_state(room):
    room_from_db = Room.query.filter_by(room_id=room).first()
    if room_from_db:
        return room_from_db.game_state


def return_admin_username(room):
    room_from_db = Room.query.filter_by(room_id=room).first()
    if room_from_db:
        return room_from_db.admin_username


def return_drawer_username(room):
    room_from_db = Room.query.filter_by(room_id=room).first()
    if room_from_db:
        return room_from_db.who_draws

def delete_room(room):
    room_from_db = Room.query.filter_by(room_id=room).first()
    os.remove("static/canvasIMG/{}.txt".format(room))
    if room_from_db:
        db.session.delete(room_from_db)
        db.session.commit()

def delete_users(room):
    users_from_db = User.query.filter_by(room_id=room).all()
    if users_from_db:
        admin = return_admin_username(room)
        for user in users_from_db:
            if user.username != admin:
                db.session.delete(user)
        db.session.commit()

def set_timer_in_db(room, turn_length):
    room_from_db = Room.query.filter_by(room_id=room).first()
    if room_from_db:
        room_from_db.timer = turn_length
        db.session.commit()

def return_time(room):
    room_from_db = Room.query.filter_by(room_id=room).first()
    if room_from_db:
        return room_from_db.timer
    return ""
        
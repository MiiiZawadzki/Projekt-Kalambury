from random import choice
from string import ascii_letters, digits
from models import Room, User
from models import db
from random import randint
import time


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

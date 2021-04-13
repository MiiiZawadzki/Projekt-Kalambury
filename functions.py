from random import choice
from string import ascii_letters, digits
from models import Room, User
from models import db
from random import randint


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
        curr_queue = room_from_db.drawing_queue
        if len(curr_queue) != 0:
            queue = curr_queue.split(';') 
            new_drawer = queue.pop(0)
            queue_string = ';'.join(queue)
            data = {'drawing_queue': queue_string}
            db.session.query(Room).filter_by(room_id=room).update(data)
        else:
            curr_drawer = room_from_db.who_draws
            users = room_from_db.users
            users_list = users.split(';')
            curr_drawer_index = users_list.index(curr_drawer)
            new_drawer = users_list[curr_drawer_index + 1]
        room_from_db.who_draws = new_drawer
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
    if user_from_db:
        print(user_from_db.score, user_from_db.id)
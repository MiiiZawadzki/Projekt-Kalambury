from random import choice
from string import ascii_letters, digits
from models import Room
from models import db


def return_current_word(room):
    room_from_db = Room.query.filter_by(room_id=room).first()
    if room_from_db:
        return room_from_db.current_word
    return ""


def change_current_word(room):
    room_from_db = Room.query.filter_by(room_id=room).first()
    if room_from_db:
        curr = room_from_db.current_word
        curr_words = room_from_db.words
        curr_words.remove(curr)
        if len(curr_words) != 0:
            room_from_db.current_word = curr_words[0]
        data = {'words': curr_words}
        db.session.query(Room).filter_by(room_id=room).update(data)
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
    room_from_db = Room.query.filter_by(room_id=room).first()
    if room_from_db:
        users_list = room_from_db.users
        if username in users_list:
            users_list.remove(username)
            data = {'users': users_list}
            db.session.query(Room).filter_by(room_id=room).update(data)
            db.session.commit()
            # delete room if is empty
            if len(room_from_db.users) == 0:
                db.session.delete(room_from_db)
                db.session.commit()


def add_user_to_db(username, room):
    room_from_db = Room.query.filter_by(room_id=room).first()
    if room_from_db:
        if room_from_db.users is None:
            data = {'users': [username]}
            db.session.query(Room).filter_by(room_id=room).update(data)
        else:
            users_list = room_from_db.users
            users_list.append(username)
            data = {'users': users_list}
            db.session.query(Room).filter_by(room_id=room).update(data)
        db.session.commit()


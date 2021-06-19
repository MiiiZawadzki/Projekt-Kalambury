from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, EqualTo, ValidationError
from flask import session
from models import Room


# custom validator to check if username is correct
def check_data(form, field):
    room_from_db = Room.query.filter_by(room_id=form.room_id.data).first()
    if room_from_db is not None:
        users_list = room_from_db.users.split(';')
        if session["username"] in users_list:
            raise ValidationError("Użytkownik o takiej nazwie już istnieje w tym pokoju")


def check_length(form, field):
    if len(field.data) > 16:
        raise ValidationError('Nazwa użytkownika jest za długa (maksimum 16 znaków)')
    if len(field.data) < 3:
        raise ValidationError('Nazwa użytkownika jest za krótka (minimum 3 znaki)')


# custom validator to check if room id is correct
def check_room(form, field):
    room_from_db = Room.query.filter_by(room_id=field.data).first()
    if room_from_db is None:
        raise ValidationError('Taki pokój nie istnieje')
    if len(field.data) != 16:
        raise ValidationError('ID pokoju musi mieć 16 znaków')


# class including fields to enter game
class IndexForm(FlaskForm):
    username = StringField('username', validators=[check_length])
    submitJoin = SubmitField('Dołącz')
    submitCreate = SubmitField('Stwórz')


# class including fields to join room
class JoinRoomForm(FlaskForm):
    room_id = StringField('pass_id', validators=[check_room, check_data])
    submit = SubmitField('Dołącz')


# class including fields to create room
class CreateRoomForm(FlaskForm):
    submit = SubmitField('Utwórz')

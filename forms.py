from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, EqualTo, ValidationError
from flask import session
from models import Room


# custom validator to check if username is correct
def check_data(form, field):
    room_from_db = Room.query.filter_by(room_id=form.room_id.data).first()
    if room_from_db is not None:
        if session["username"] in room_from_db.users:
            raise ValidationError("Użytkownik o takiej nazwie już istnieje w tym pokoju")
        if room_from_db.game_state == "game_in_progress":
            raise ValidationError("Gra jest w trakcie rozgrywki, dołącz za chwile")


# custom validator to check if room id is correct
def check_room(form, field):
    room_from_db = Room.query.filter_by(room_id=field.data).first()
    if room_from_db is None:
        raise ValidationError('Taki pokój nie istnieje')


# class including fields to enter game
class IndexForm(FlaskForm):
    username = StringField('username', validators=[InputRequired()])
    submitJoin = SubmitField('Dołącz')
    submitCreate = SubmitField('Stwórz')


# class including fields to join room
class JoinRoomForm(FlaskForm):
    room_id = StringField('pass_id', validators=[Length(min=16, max=16), check_room, check_data])
    submit = SubmitField('Dołącz')


# class including fields to create room
class CreateRoomForm(FlaskForm):
    submit = SubmitField('Utwórz')

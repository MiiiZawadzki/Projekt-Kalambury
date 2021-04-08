from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


# Room model
class Room(db.Model):
    __tablename__ = 'rooms'
    id = db.Column(db.Integer(), primary_key=True)
    room_id = db.Column(db.Text(), unique=True, nullable=False)
    admin_username = db.Column(db.Text(), nullable=False)
    users = db.Column(db.ARRAY(db.Text()))
    current_word = db.Column(db.Text())
    words = db.Column(db.ARRAY(db.Text()))
    who_draws = db.Column(db.Text())
    drawing_queue = db.Column(db.ARRAY(db.Text()))
    turn_count = db.Column(db.Integer(), nullable=False)
    turn_length = db.Column(db.Integer(), nullable=False)
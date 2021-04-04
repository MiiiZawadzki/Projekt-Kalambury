from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


# Room model
class Room(db.Model):
    __tablename__ = 'rooms'
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Text(), unique=True, nullable=False)
    admin_username = db.Column(db.Text(), nullable=False)
    users = db.Column(db.ARRAY(db.Text()))
    current_word = db.Column(db.Text())
    words = db.Column(db.ARRAY(db.Text()))

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


# Room model
class Room(db.Model):
    __tablename__ = 'rooms'
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.String(16), unique=True, nullable=False)
    admin_username = db.Column(db.String(), nullable=False)
    users = db.Column(db.ARRAY(db.String()))
    current_word = db.Column(db.String())
    words = db.Column(db.ARRAY(db.String()))

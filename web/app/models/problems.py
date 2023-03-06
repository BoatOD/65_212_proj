from app import db
from sqlalchemy_serializer import SerializerMixin


class problems(db.Model, SerializerMixin):
    __tablename__ = "problems"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    message = db.Column(db.String(280))
    email = db.Column(db.String(50))
    date = db.Column(db.String(60))
    avatar_url = db.Column(db.String(100))
    coor_map = db.Column(db.Integer)

    def __init__(self, name, message, email , date, avatar_url, lat, rot):
        self.name = name
        self.message = message
        self.email = email
        self.date = date
        self.avatar_url = avatar_url
        self.lat = lat
        self.rot = rot


    def update(self, name, message, email , date, avatar_url, lat, rot):
        self.name = name
        self.message = message
        self.email = email
        self.date = date
        self.avatar_url = avatar_url
        self.lat = lat
        self.rot = rot
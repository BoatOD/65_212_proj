from app import db
from sqlalchemy_serializer import SerializerMixin


class review(db.Model, SerializerMixin):
    __tablename__ = "review"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    message = db.Column(db.String(280))
    email = db.Column(db.String(50))
    date = db.Column(db.String(60))
    avatar_url = db.Column(db.String(100))
    lat = db.Column(db.Integer)
    lot = db.Column(db.Integer)

    def __init__(self, name, message, email , date, avatar_url, lat, lot):
        self.name = name
        self.message = message
        self.email = email
        self.date = date
        self.avatar_url = avatar_url
        self.lat = lat
        self.lot = lot


    def update(self, name, message, email , date, avatar_url, lat, lot):
        self.name = name
        self.message = message
        self.email = email
        self.date = date
        self.avatar_url = avatar_url
        self.lat = lat
        self.lot = lot
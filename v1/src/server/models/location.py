# src/server/models/location.py

import datetime

from src.server import db


class Location(db.Model):
    """ Location Model (GPS tracking data points) """
    __tablename__ = 'locations'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    card_id = db.Column(db.Integer, db.ForeignKey('cards.id'), nullable=False)
    lat = db.Column(db.Numeric(10, 8), nullable=False)
    lng = db.Column(db.Numeric(11, 8), nullable=False)
    speed = db.Column(db.Numeric(5, 2), default=0.00)
    battery = db.Column(db.SmallInteger, nullable=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    sos_button_pressed = db.Column(db.SmallInteger, nullable=False, default=0)

    def __repr__(self):
        return f'<Location card={self.card_id} lat={self.lat} lng={self.lng}>'

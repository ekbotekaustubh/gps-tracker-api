# src/server/models/card.py

import datetime

from src.server import db


class Card(db.Model):
    """ Card Model (GPS Tracking Devices) """
    __tablename__ = 'cards'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    imei_number = db.Column(db.String(50), unique=True, nullable=False)
    sim_mobile = db.Column(db.String(20), nullable=False)
    company = db.Column(db.String(100), nullable=True)
    model = db.Column(db.String(100), nullable=True)
    status = db.Column(db.SmallInteger, nullable=False, default=1)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    member = db.relationship('CardMember', backref=db.backref('card', lazy=True), uselist=False)
    locations = db.relationship('Location', backref=db.backref('card', lazy=True))

    def __repr__(self):
        return f'<Card {self.name} IMEI={self.imei_number}>'

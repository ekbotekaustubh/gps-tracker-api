# src/server/models/country.py

import datetime

from src.server import db


class Country(db.Model):
    """ Country Model """
    __tablename__ = 'countries'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    country_code = db.Column(db.String(10), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    states = db.relationship('State', backref=db.backref('country', lazy=True))
    cities = db.relationship('City', backref=db.backref('country', lazy=True))

    def __repr__(self):
        return f'<Country {self.name}>'

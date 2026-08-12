# src/server/models/state.py

import datetime

from src.server import db


class State(db.Model):
    """ State Model """
    __tablename__ = 'states'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    state_code = db.Column(db.String(10), nullable=False)
    country_id = db.Column(db.Integer, db.ForeignKey('countries.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    cities = db.relationship('City', backref=db.backref('state', lazy=True))

    def __repr__(self):
        return f'<State {self.name}>'

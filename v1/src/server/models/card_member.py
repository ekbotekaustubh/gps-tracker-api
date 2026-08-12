# src/server/models/card_member.py

import datetime

from src.server import db


class CardMember(db.Model):
    """ Card Member Model """
    __tablename__ = 'card_members'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), nullable=True)
    mobile = db.Column(db.String(20), nullable=False)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=False)
    address_line_1 = db.Column(db.String(255), nullable=True)
    address_line_2 = db.Column(db.String(255), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    pincode = db.Column(db.String(20), nullable=True)
    country_id = db.Column(db.Integer, db.ForeignKey('countries.id'), nullable=False)
    state_id = db.Column(db.Integer, db.ForeignKey('states.id'), nullable=False)
    city_id = db.Column(db.Integer, db.ForeignKey('cities.id'), nullable=True)
    card_id = db.Column(db.Integer, db.ForeignKey('cards.id'), unique=True, nullable=True)
    emergency_contact_1 = db.Column(db.String(20), nullable=False)
    emergency_contact_2 = db.Column(db.String(20), nullable=True)
    emergency_contact_3 = db.Column(db.String(20), nullable=True)
    status = db.Column(db.SmallInteger, nullable=False, default=1)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    branch = db.relationship('Branch', backref=db.backref('card_members', lazy=True))
    country = db.relationship('Country', backref=db.backref('card_members', lazy=True))
    state = db.relationship('State', backref=db.backref('card_members', lazy=True))
    city_ref = db.relationship('City', backref=db.backref('card_members', lazy=True))

    def __repr__(self):
        return f'<CardMember {self.name}>'

# src/server/models/branch.py

import datetime

from src.server import db


class Branch(db.Model):
    """ Branch Model """
    __tablename__ = 'branches'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    org_id = db.Column(db.Integer, db.ForeignKey('organizations.id'), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    address_line_1 = db.Column(db.String(255), nullable=False)
    address_line_2 = db.Column(db.String(255), nullable=True)
    city = db.Column(db.String(100), nullable=False)
    pincode = db.Column(db.String(20), nullable=False)
    country_id = db.Column(db.Integer, db.ForeignKey('countries.id'), nullable=False)
    state_id = db.Column(db.Integer, db.ForeignKey('states.id'), nullable=False)
    city_id = db.Column(db.Integer, db.ForeignKey('cities.id'), nullable=True)
    is_head_office = db.Column(db.SmallInteger, nullable=False, default=0)
    mobile = db.Column(db.String(20), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    status = db.Column(db.SmallInteger, nullable=False, default=1)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    country = db.relationship('Country', backref=db.backref('branches', lazy=True))
    state = db.relationship('State', backref=db.backref('branches', lazy=True))
    city_ref = db.relationship('City', backref=db.backref('branches', lazy=True))

    def __repr__(self):
        return f'<Branch {self.name}>'

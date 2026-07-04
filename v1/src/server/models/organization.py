# src/server/models/organization.py

import datetime

from src.server import db


class Organization(db.Model):
    """organization Model"""

    __tablename__ = 'organizations'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    name = db.Column(db.String(100), nullable=False)

    address_line_1 = db.Column(db.String(255), nullable=False)

    address_line_2 = db.Column(db.String(255))

    city = db.Column(db.String(100), nullable=False)

    pincode = db.Column(db.String(10), nullable=False)

    country_id = db.Column(
        db.Integer,
        db.ForeignKey('countries.id'),
        nullable=False
    )

    state_id = db.Column(
        db.Integer,
        db.ForeignKey('states.id'),
        nullable=False
    )

    status = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.datetime.utcnow
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow
    )

    def __repr__(self):
        return f'<Organization {self.name}>'
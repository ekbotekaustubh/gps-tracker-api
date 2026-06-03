# src/server/models/organization.py

import datetime

from src.server import db


class Organization(db.Model):
    """ Organization Model """
    __tablename__ = 'organizations'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(150), nullable=False)
    status = db.Column(db.SmallInteger, nullable=False, default=1)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    branches = db.relationship('Branch', backref=db.backref('organization', lazy=True))

    def __repr__(self):
        return f'<Organization {self.name}>'

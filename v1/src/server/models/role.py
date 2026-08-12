# src/server/models/role.py

import datetime

from src.server import db


class Role(db.Model):
    """ Role Model """
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    status = db.Column(db.SmallInteger, nullable=False, default=1)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    permissions = db.relationship('Permission', secondary='role_permissions', backref=db.backref('roles', lazy=True))

    def __repr__(self):
        return f'<Role {self.name}>'

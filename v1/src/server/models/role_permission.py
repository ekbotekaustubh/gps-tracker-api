# src/server/models/role_permission.py

from src.server import db


class RolePermission(db.Model):
    """ Role-Permission association table """
    __tablename__ = 'role_permissions'

    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), primary_key=True, nullable=False)
    permission_id = db.Column(db.Integer, db.ForeignKey('permissions.id'), primary_key=True, nullable=False)

    def __repr__(self):
        return f'<RolePermission role={self.role_id} permission={self.permission_id}>'

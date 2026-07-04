from flask import request
from flask_restx import Resource, fields, Namespace

from src.server import db
from src.server.models import Role

# Create namespace
roles_ns = Namespace('roles', description='Roles operations')

role_model = roles_ns.model('Role', {
    'id': fields.Integer(description='Role ID'),
    'name': fields.String(required=True, description='Role name'),
    'status': fields.Boolean(description='Role status'),
    'created_at': fields.DateTime(description='Created at'),
    'updated_at': fields.DateTime(description='Updated at')
})


@roles_ns.route('', '/<int:role_id>')
class RolesAPI(Resource):
    """Single Resource to handle collection and item endpoints for roles"""

    @roles_ns.expect(role_model)
    @roles_ns.response(201, 'Role created successfully')
    @roles_ns.response(409, 'Role already exists')
    @roles_ns.response(500, 'Internal server error')
    def post(self):
        """Create Role"""
        post_data = request.get_json() or {}
        try:
            role = Role.query.filter_by(name=post_data.get('name')).first()
            if role:
                return {'status': 'fail', 'message': 'Role already exists.'}, 409

            role = Role(
                name=post_data.get('name'),
                status=post_data.get('status', 1)
            )

            db.session.add(role)
            db.session.commit()

            return {'status': 'success', 'message': 'Role added successfully.', 'data': {'id': role.id}}, 201

        except Exception as e:
            db.session.rollback()
            return {'status': 'fail', 'message': 'Some error occurred: ' + str(e)}, 500
        finally:
            db.session.close()

    @roles_ns.response(200, 'Success', [role_model])
    @roles_ns.response(500, 'Internal server error')
    def get(self, role_id=None):
        """Get role list, role by name (query param 'name') or role by id if role_id provided"""
        try:
            # If role_id provided, return that role
            if role_id:
                role = Role.query.filter_by(id=role_id).first()
                if not role:
                    return {'status': 'fail', 'message': 'Role not found.'}, 404

                return {
                    'status': 'success',
                    'message': 'role retrieved successfully.',
                    'data': {
                        'id': role.id,
                        'name': role.name,
                        'status': role.status,
                        'created_at': role.created_at.isoformat() if role.created_at else None,
                        'updated_at': role.updated_at.isoformat() if role.updated_at else None
                    }
                }, 200

            # Query by name if provided
            role_name = request.args.get('name')
            if role_name:
                role = Role.query.filter_by(name=role_name).first()
                if not role:
                    return {'status': 'fail', 'message': 'Role not found.'}, 404

                return {
                    'status': 'success',
                    'message': 'role retrieved successfully.',
                    'data': {
                        'id': role.id,
                        'name': role.name,
                        'status': role.status,
                        'created_at': role.created_at.isoformat() if role.created_at else None,
                        'updated_at': role.updated_at.isoformat() if role.updated_at else None,
                    }
                }, 200

            # Otherwise return list
            roles = Role.query.all()
            roles_list = [
                {
                    'id': r.id,
                    'name': r.name,
                    'status': r.status,
                    'created_at': r.created_at.isoformat() if r.created_at else None,
                    'updated_at': r.updated_at.isoformat() if r.updated_at else None,
                }
                for r in roles
            ]

            return {'status': 'success', 'message': 'roles retrieved successfully.', 'data': roles_list}, 200

        except Exception as e:
            return {'status': 'fail', 'message': 'Error retrieving roles: ' + str(e)}, 500

    @roles_ns.expect(role_model)
    @roles_ns.response(200, 'Role updated successfully')
    @roles_ns.response(404, 'Role not found')
    @roles_ns.response(500, 'Internal server error')
    def put(self, role_id):
        """Update role (requires role_id)"""
        post_data = request.get_json() or {}
        try:
            role = Role.query.filter_by(id=role_id).first()
            if not role:
                return {'status': 'fail', 'message': 'Role not found.'}, 404

            role.name = post_data.get('name', role.name)
            role.status = post_data.get('status', role.status)

            db.session.commit()
            return {'status': 'success', 'message': 'Role updated successfully.'}, 200

        except Exception as e:
            db.session.rollback()
            return {'status': 'fail', 'message': 'Some error occurred: ' + str(e)}, 500
        finally:
            db.session.close()

    @roles_ns.response(200, 'Role deleted successfully')
    @roles_ns.response(404, 'Role not found')
    @roles_ns.response(500, 'Internal server error')
    def delete(self, role_id):
        """Delete role (requires role_id)"""
        try:
            role = Role.query.filter_by(id=role_id).first()
            if not role:
                return {'status': 'fail', 'message': 'Role not found.'}, 404

            db.session.delete(role)
            db.session.commit()
            return {'status': 'success', 'message': 'Role deleted successfully.'}, 200

        except Exception as e:
            db.session.rollback()
            return {'status': 'fail', 'message': 'Some error occurred: ' + str(e)}, 500
        finally:
            db.session.close()

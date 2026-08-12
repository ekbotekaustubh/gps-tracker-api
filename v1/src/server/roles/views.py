from flask import request
from flask_restx import Resource, fields, Namespace

from src.server import db
from src.server.models import Role
from src.server.role_permission.utilty import authorize

# Swagger Namespace
roles_ns = Namespace('roles', description='Roles operations')

role_model = roles_ns.model('Role', {
    'id': fields.Integer(description='Role ID'),
    'name': fields.String(required=True, description='Role Name'),
    'status': fields.Boolean(required=True, description='Status'),
    'created_at': fields.DateTime(description='Created At'),
    'updated_at': fields.DateTime(description='Updated At')
})


@roles_ns.route('')
class RolesListAPI(Resource):
    """Collection endpoint: POST (create) and GET (list or query by name)"""

    @roles_ns.expect(role_model)
    @roles_ns.response(201, 'Role created successfully')
    @roles_ns.response(409, 'Role already exists')
    @roles_ns.response(500, 'Internal server error')
    @roles_ns.doc(security='Bearer Auth')
    @authorize('role.create')  # Example permission key, adjust as needed
    def post(self):
        """Create Role"""

        post_data = request.get_json()

        try:
            role = Role.query.filter_by(
                name=post_data.get('name')
            ).first()

            if role:
                responseObject = {
                    'status': 'fail',
                    'message': 'Role already exists.'
                }
                return responseObject, 409

            role = Role(
                name=post_data.get('name'),
                status=post_data.get('status')
            )

            db.session.add(role)
            db.session.commit()

            responseObject = {
                'status': 'success',
                'message': 'Role added successfully.',
                'data': {'id': role.id}
            }

            return responseObject, 201

        except Exception as e:
            db.session.rollback()
            responseObject = {'status': 'fail', 'message': 'Some error occurred: ' + str(e)}
            return responseObject, 500
        finally:
            db.session.close()

    @roles_ns.response(200, 'Success', [role_model])
    @roles_ns.response(500, 'Internal server error')
    @roles_ns.doc(security='Bearer Auth')
    @authorize('role.view')  # Example permission key, adjust as needed
    def get(self):
        """Get role list or role by name (query param 'name')"""

        try:
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


@roles_ns.route('/<int:role_id>')
class RoleAPI(Resource):
    """Item endpoint: GET, PUT, DELETE for a single role"""

    @roles_ns.response(200, 'Success', role_model)
    @roles_ns.response(404, 'role not found')
    @roles_ns.response(500, 'Internal server error')
    @roles_ns.doc(security='Bearer Auth')
    @authorize('role.view')  # Example permission key, adjust as needed
    def get(self, role_id):
        """Get role details by ID"""
        try:
            role = Role.query.filter_by(id=role_id).first()
            if not role:
                return {'status': 'fail', 'message': 'role not found.'}, 404

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

        except Exception as e:
            return {'status': 'fail', 'message': 'Error retrieving role: ' + str(e)}, 500

    @roles_ns.expect(role_model)
    @roles_ns.response(200, 'role updated successfully')
    @roles_ns.response(404, 'role not found')
    @roles_ns.response(500, 'Internal server error')
    @roles_ns.doc(security='Bearer Auth')
    @authorize('role.update')  # Example permission key, adjust as needed
    def put(self, role_id):
        """Update role"""
        post_data = request.get_json()
        try:
            role = Role.query.filter_by(id=role_id).first()
            if not role:
                return {'status': 'fail', 'message': 'role not found.'}, 404

            role.name = post_data.get('name', role.name)
            role.status = post_data.get('status', role.status)

            db.session.commit()
            return {'status': 'success', 'message': 'role updated successfully.'}, 200

        except Exception as e:
            db.session.rollback()
            return {'status': 'fail', 'message': 'Some error occurred: ' + str(e)}, 500
        finally:
            db.session.close()

    @roles_ns.response(200, 'role deleted successfully')
    @roles_ns.response(404, 'role not found')
    @roles_ns.response(500, 'Internal server error')
    @roles_ns.doc(security='Bearer Auth')
    @authorize('role.delete')  # Example permission key, adjust as needed
    def delete(self, role_id):
        """Delete role"""
        try:
            role = Role.query.filter_by(id=role_id).first()
            if not role:
                return {'status': 'fail', 'message': 'role not found.'}, 404

            db.session.delete(role)
            db.session.commit()
            return {'status': 'success', 'message': 'role deleted successfully.'}, 200

        except Exception as e:
            db.session.rollback()
            return {'status': 'fail', 'message': 'Some error occurred: ' + str(e)}, 500
        finally:
            db.session.close()

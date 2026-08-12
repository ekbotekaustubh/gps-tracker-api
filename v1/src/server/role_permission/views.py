from pyclbr import Class

from flask import request
from flask_restx import Resource, fields, Namespace
from src.server import db
from src.server.models import Role, Permission, RolePermission
import traceback
from src.server.role_permission.utilty import authorize

RolePermissions_ns = Namespace('role_permissions', description = "role-permission operations")

# Models for API documentation
role_permission_input_model = RolePermissions_ns.model('RolePermissionInput', {
    'role_id': fields.Integer(required=True, description='Role ID'),
    'permission_id': fields.Integer(required=True, description='Permission ID')
})

role_permission_response_model = RolePermissions_ns.model('RolePermissionResponse', {
    'role_id': fields.Integer(description='Role ID'),
    'role_name': fields.String(description='Role name'),
    'permission_id': fields.Integer(description='Permission ID'),
    'permission_name': fields.String(description='Permission name'),
    'permission_key': fields.String(description='Permission key')
})

role_permissions_list_model = RolePermissions_ns.model('RolePermissionsList', {
    'role_id': fields.Integer(description='Role ID'),
    'role_name': fields.String(description='Role name'),
    'permissions': fields.List(fields.Nested(role_permission_response_model), description='List of permissions')
})


@RolePermissions_ns.route('/')
class RolePermissionListAPI(Resource):
    @RolePermissions_ns.expect(role_permission_input_model)
    @RolePermissions_ns.response(201, 'Permission assigned to role successfully', role_permission_response_model)
    @RolePermissions_ns.response(400, 'Invalid input')
    @RolePermissions_ns.response(404, 'Role or Permission not found')
    @RolePermissions_ns.response(409, 'Role already has this permission')
    @RolePermissions_ns.doc(security='Bearer Auth')
    @authorize('role_permissions.create')  # Example permission key, adjust as needed
    def post(self):
        """Assign a permission to a role"""
        try:
            data = request.get_json()
            
            if not data:
                return {
                    'status': 'fail',
                    'message': 'No JSON data provided'
                }, 400
            
            role_id = data.get('role_id')
            permission_id = data.get('permission_id',[])
            
            # Validate required fields
            if not role_id or not permission_id:
                return {
                    'status': 'fail',
                    'message': 'Missing required fields: role_id and permission_id'
                }, 400
            
            # Check if role exists
            role = Role.query.get(role_id)
            if not role:
                return {
                    'status': 'fail',
                    'message': f'Role with ID {role_id} not found'
                }, 404
            
            # Check if permission exists
            permission = Permission.query.get(permission_id)
            if not permission:
                return {
                    'status': 'fail',
                    'message': f'Permission with ID {permission_id} not found'
                }, 404
            
            # Check if role already has this permission
            existing = RolePermission.query.filter_by(
                role_id=role_id,
                permission_id=permission_id
            ).first()
            
            if existing:
                return {
                    'status': 'fail',
                    'message': 'Role already has this permission'
                }, 409
            
            # Create role-permission association
            role_permission = RolePermission(role_id=role_id, permission_id=permission_id)
            db.session.add(role_permission)
            db.session.commit()
            
            return {
                'status': 'success',
                'message': 'Permission assigned to role successfully',
                'data': {
                    'role_id': role.id,
                    'role_name': role.name,
                    'permission_id': permission.id,
                    'permission_name': permission.name,
                    'permission_key': permission.permission_key
                }
            }, 201
            
        except Exception as e:
            db.session.rollback()
            print(f"Error assigning permission to role: {traceback.format_exc()}")
            return {
                'status': 'fail',
                'message': f'Error assigning permission: {str(e)}'
            }, 500

    @RolePermissions_ns.response(200, 'List of all role-permission associations')
    @RolePermissions_ns.doc(security='Bearer Auth')
    @authorize('role_permissions.view')  # Example permission key, adjust as needed
    def get(self):
        """Get all role-permission associations"""
        try:
            role_permissions = RolePermission.query.all()
            
            result = []
            for rp in role_permissions:
                role = Role.query.get(rp.role_id)
                permission = Permission.query.get(rp.permission_id)
                
                if role and permission:
                    result.append({
                        'role_id': role.id,
                        'role_name': role.name,
                        'permission_id': permission.id,
                        'permission_name': permission.name,
                        'permission_key': permission.permission_key
                    })
            
            return {
                'status': 'success',
                'message': 'Role-permission associations retrieved successfully',
                'data': result,
                'total': len(result)
            }, 200
            
        except Exception as e:
            print(f"Error retrieving role-permissions: {traceback.format_exc()}")
            return {
                'status': 'fail',
                'message': f'Error retrieving role-permissions: {str(e)}'
            }, 500

    @RolePermissions_ns.expect(RolePermissions_ns.model('RolePermissionsUpdate', {
        'role_id': fields.Integer(required=True, description='Role ID'),
        'permission_ids': fields.List(fields.Integer, required=True, description='List of permission IDs')
    }))
    @RolePermissions_ns.response(200, 'Role permissions updated successfully')
    @RolePermissions_ns.response(400, 'Invalid input')
    @RolePermissions_ns.response(404, 'Role not found')
    @RolePermissions_ns.doc(security='Bearer Auth')
    @authorize('role_permissions.update')  # Example permission key, adjust as needed
    def put(self):
        """Update all permissions for a role (replaces existing permissions)"""
        try:
            data = request.get_json()
            
            if not data:
                return {
                    'status': 'fail',
                    'message': 'No JSON data provided'
                }, 400
            
            role_id = data.get('role_id')
            permission_ids = data.get('permission_ids', [])
            
            # Validate required fields
            if not role_id:
                return {
                    'status': 'fail',
                    'message': 'Missing required field: role_id'
                }, 400
            
            # Check if role exists
            role = Role.query.get(role_id)
            if not role:
                return {
                    'status': 'fail',
                    'message': f'Role with ID {role_id} not found'
                }, 404
            
            # Validate all permission IDs exist
            for perm_id in permission_ids:
                permission = Permission.query.get(perm_id)
                if not permission:
                    return {
                        'status': 'fail',
                        'message': f'Permission with ID {perm_id} not found'
                    }, 404
            
            # Delete all existing permissions for this role
            RolePermission.query.filter_by(role_id=role_id).delete()
            
            # Add new permissions
            added_permissions = []
            for perm_id in permission_ids:
                permission = Permission.query.get(perm_id)
                role_permission = RolePermission(role_id=role_id, permission_id=perm_id)
                db.session.add(role_permission)
                added_permissions.append({
                    'permission_id': permission.id,
                    'permission_name': permission.name,
                    'permission_key': permission.permission_key
                })
            
            db.session.commit()
            
            return {
                'status': 'success',
                'message': 'Role permissions updated successfully',
                'data': {
                    'role_id': role.id,
                    'role_name': role.name,
                    'permissions': added_permissions,
                    'total_permissions': len(added_permissions)
                }
            }, 200
            
        except Exception as e:
            db.session.rollback()
            print(f"Error updating role permissions: {traceback.format_exc()}")
            return {
                'status': 'fail',
                'message': f'Error updating role permissions: {str(e)}'
            }, 500


@RolePermissions_ns.route('/<int:role_id>')
class RolePermissionsAPI(Resource):
    @RolePermissions_ns.response(200, 'List of permissions for a role', role_permissions_list_model)
    @RolePermissions_ns.response(404, 'Role not found')
    @RolePermissions_ns.doc(security='Bearer Auth')
    @authorize('role_permissions.view')  # Example permission key, adjust as needed
    def get(self, role_id):
        """Get all permissions for a specific role"""
        try:
            role = Role.query.get(role_id)
            
            if not role:
                return {
                    'status': 'fail',
                    'message': f'Role with ID {role_id} not found'
                }, 404
            
            role_permissions = RolePermission.query.filter_by(role_id=role_id).all()
            
            permissions = []
            for rp in role_permissions:
                permission = Permission.query.get(rp.permission_id)
                if permission:
                    permissions.append({
                        'permission_id': permission.id,
                        'permission_name': permission.name,
                        'permission_key': permission.permission_key
                    })
            
            return {
                'status': 'success',
                'message': f'Permissions for role {role.name} retrieved successfully',
                'data': {
                    'role_id': role.id,
                    'role_name': role.name,
                    'permissions': permissions,
                    'total_permissions': len(permissions)
                }
            }, 200
            
        except Exception as e:
            print(f"Error retrieving permissions for role: {traceback.format_exc()}")
            return {
                'status': 'fail',
                'message': f'Error retrieving role permissions: {str(e)}'
            }, 500



    @RolePermissions_ns.response(200, 'Permission removed from role successfully')
    @RolePermissions_ns.response(404, 'Role-permission association not found')
    @RolePermissions_ns.doc(security='Bearer Auth')
    @authorize('role_permissions.delete')  # Example permission key, adjust as needed
    def delete(self, role_id, permission_id):
        """Remove a permission from a role"""
        try:
            role_permission = RolePermission.query.filter_by(
                role_id=role_id,
                permission_id=permission_id
            ).first()
            
            if not role_permission:
                return {
                    'status': 'fail',
                    'message': f'Permission {permission_id} not found for role {role_id}'
                }, 404
            
            db.session.delete(role_permission)
            db.session.commit()
            
            return {
                'status': 'success',
                'message': 'Permission removed from role successfully',
                'data': {
                    'role_id': role_id,
                    'permission_id': permission_id
                }
            }, 200
            
        except Exception as e:
            db.session.rollback()
            print(f"Error removing permission from role: {traceback.format_exc()}")
            return {
                'status': 'fail',
                'message': f'Error removing permission: {str(e)}'
            }, 500
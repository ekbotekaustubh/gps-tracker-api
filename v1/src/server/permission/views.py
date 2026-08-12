from pyclbr import Class

from flask import request
from flask_restx import Resource, fields, Namespace
from src.server import db
from src.server.models import Permission
import traceback
from src.server.role_permission.utilty import authorize


Permissions_ns = Namespace('permissions', description = "permission operations")

permission_input_model = Permissions_ns.model('PermissionInput', {
    'name': fields.String(required=True, description='Permission name'),
    'permission_key': fields.String(required=True, description='Permission key (unique)'),
    'description': fields.String(description='Permission description'),
    'status': fields.Integer(description='Permission status (0=inactive, 1=active)', default=1)
})

permission_response_model = Permissions_ns.model('PermissionResponse', {
    'id': fields.Integer(description='Permission ID'),
    'name': fields.String(description='Permission name'),
    'permission_key': fields.String(description='Permission key'),
    'description': fields.String(description='Permission description'),
    'status': fields.Integer(description='Permission status'),
    'created_at': fields.DateTime(description='Permission creation timestamp'),
    'updated_at': fields.DateTime(description='Permission update timestamp')
})
permision_model = Permissions_ns.model('PermissionResponse', {
    'id': fields.Integer(description='Permission ID'),
    'name': fields.String(description='Permission name'),
    'permission_key': fields.String(description='Permission key'),
    'description': fields.String(description='Permission description'),
    'status': fields.Integer(description='Permission status')
})


@Permissions_ns.route('/')
class PermissionListAPI(Resource):
    @Permissions_ns.expect(permission_input_model)
    @Permissions_ns.response(201, 'Permission created successfully', permission_response_model)
    @Permissions_ns.response(400, 'Invalid input')
    @Permissions_ns.response(409, 'Permission key already exists')
    @authorize('permission.create')  # Example permission key, adjust as needed
    def post(self):
        """Create a new permission"""
        try:
            post_data = request.get_json()
            
            # Validate required fields
            if not post_data.get('name') or not post_data.get('permission_key'):
                responseObject = {
                    'status': 'fail',
                    'message': 'Missing required fields: name and permission_key'
                }
                return responseObject, 400
            
            # Check if permission_key already exists
            existing_permission = Permission.query.filter_by(
                permission_key=post_data.get('permission_key')
            ).first()
            
            if existing_permission:
                responseObject  = {
                    'status': 'fail',
                    'message': 'Permission with this key already exists'
                }
                return responseObject, 409
            
            # Create new permission
            permission = Permission(
                name=post_data.get('name'),
                permission_key=post_data.get('permission_key'),
                description=post_data.get('description'),
                status=post_data.get('status', 1)
            )
            
            db.session.add(permission)
            db.session.commit()
            
            responseObject = {
                'status': 'success',
                'message': 'Permission created successfully',
                'data': {
                    'id': permission.id,
                    'name': permission.name,
                    'permission_key': permission.permission_key,
                    'description': permission.description,
                    'status': permission.status,
                     'created_at': permission.created_at.isoformat() if permission.created_at else None,
                    'updated_at': permission.updated_at.isoformat() if permission.updated_at else None
                    }
            }
            return responseObject, 201
            
        except Exception as e:
            db.session.rollback()
            traceback.print_exc()
            responseObject = {
                'status': 'fail',
                'message': f'Error creating permission: {str(e)}'
            }
            return responseObject, 500
    
    @Permissions_ns.response(200,'Success',[permision_model])
    @Permissions_ns.response(500, 'internal server error')    
    @authorize('permission.view')  # Example permission key, adjust as needed
    def get(self):
        """Get list of all permissions"""
        try:
            permisions = Permission.query.all()
            permisions_list = [
                {
                   'id': permision.id,
                    'name':permision.name,
                    'permision_key':permision.permission_key,
                    'description':permision.description,
                    'status':permision.status       
                }
                
                for permision in permisions
            ]
           
            return {
                'status': 'success',
                'message': 'Permision retrieved successfully.',
                'data': permisions_list
            }, 200
        except Exception as e:
            return {
                'status': 'fail',
                'message': f'Error retrieving countries: {str(e)}'
            }, 500
        
@Permissions_ns.route('/<int:permission_id>') 
class PermissionDetailAPI(Resource):
    @authorize('permission.view')  # Example permission key, adjust as needed
    @Permissions_ns.response(200, 'Success', permision_model)
    @Permissions_ns.response(404, 'Permission not found')  
    @Permissions_ns.response(500, 'Internal server error')
    def get(self, permission_id):
        """Get a specific permission by ID"""
        try:
            permission = Permission.query.filter_by(id=permission_id).first()
            if not permission:
                return {
                    'status': 'fail',
                    'message': 'Permission not found.'
                }, 404

            return {
                'status': 'success',
                'message': 'Permission retrieved successfully.',
                'data': {
                    'id': permission.id,
                    'name': permission.name,
                    'permission_key': permission.permission_key,
                    'description': permission.description,
                    'status': permission.status
                }
            }, 200
        except Exception as e:
            return {
                'status': 'fail',
                'message': f'Error retrieving permission: {str(e)}'
            }, 500 
    @Permissions_ns.expect(permission_input_model)
    @Permissions_ns.response(200, 'Permission updated successfully')
    @Permissions_ns.response(400, 'Invalid input')
    @Permissions_ns.response(404, 'Permission not found')  
    @authorize('permission.update')  # Example permission key, adjust as needed 
    def put(self, permission_id):
        """Update a specific permission by ID"""
        try:
            permission = Permission.query.filter_by(id=permission_id).first()
            if not permission:
                return {
                    'status': 'fail',
                    'message': 'Permission not found.'
                }, 404
            
            post_data = request.get_json()
            permission.name = post_data.get('name', permission.name)
            permission.permission_key = post_data.get('permission_key', permission.permission_key)
            permission.description = post_data.get('description', permission.description)
            permission.status = post_data.get('status', permission.status)
            
            db.session.commit()
            
            return {
                'status': 'success',
                'message': 'Permission updated successfully.',
                'data': {
                    'id': permission.id,
                    'name': permission.name,
                    'permission_key': permission.permission_key,
                    'description': permission.description,
                    'status': permission.status
                }
            }, 200
        except Exception as e:
            db.session.rollback()
            return {
                'status': 'fail',
                'message': f'Error updating permission: {str(e)}'
            }, 500

    @Permissions_ns.response(200, 'Permission deleted successfully')
    @Permissions_ns.response(404, 'Permission not found')
    @authorize('permission.delete')  # Example permission key, adjust as needed
    def delete(self, permission_id):
        """Delete a specific permission by ID"""
        try:
            permission = Permission.query.filter_by(id=permission_id).first()
            if not permission:
                return {
                    'status': 'fail',
                    'message': 'Permission not found.'
                }, 404
            
            db.session.delete(permission)
            db.session.commit()
            
            return {
                'status': 'success',
                'message': 'Permission deleted successfully.'
            }, 200
        except Exception as e:
            db.session.rollback()
            return {
                'status': 'fail',
                'message': f'Error deleting permission: {str(e)}'
            }, 500


from flask import request
from flask_restx import Resource, fields

from src.server import bcrypt, db
from src.server.models import User, BlacklistToken
from src.server import auth_ns

register_model = auth_ns.model('Register', {
    'name': fields.String(required=True, description='Full name'),
    'email': fields.String(required=True, description='Email address'),
    'mobile': fields.String(required=True, description='Mobile number'),
    'branch_id': fields.Integer(required=True, description='Branch ID'),
    'role_id': fields.Integer(required=True, description='Role ID'),
    'country_id': fields.Integer(required=True, description='Country ID'),
    'state_id': fields.Integer(required=True, description='State ID'),
    'username': fields.String(required=True, description='Username'),
    'password': fields.String(required=True, description='Password'),
    'address_line_1': fields.String(description='Address line 1'),
    'address_line_2': fields.String(description='Address line 2'),
    'city_id': fields.Integer(description='City ID'),
    'pincode': fields.String(description='Pincode'),
})


@auth_ns.route('/users/<int:user_id>')
class UsersAPI(Resource):
    @auth_ns.doc(security='Bearer Auth')
    @auth_ns.response(200, 'Success')
    @auth_ns.response(401, 'Invalid token')
    @auth_ns.response(404, 'User not found')
    def get(self, user_id):
        """Get user by user ID"""
        auth_header = request.headers.get('Authorization')
        if auth_header:
            try:
                auth_token = auth_header.split(" ")[1]
            except IndexError:
                responseObject = {
                    'status': 'fail',
                    'message': 'Bearer token malformed.'
                }
                return responseObject, 401
        else:
            auth_token = ''
        if auth_token:
            resp = User.decode_auth_token(auth_token)
            if not isinstance(resp, str):
                try:
                    user = User.query.filter_by(id=user_id).first()
                    if user:
                        responseObject = {
                            'status': 'success',
                            'user_id': user.id,
                            'name': user.name,
                            'email': user.email,
                            'mobile': user.mobile,
                            'username': user.username,
                            'branch_id': user.branch_id,
                            'role_id': user.role_id,
                            'country_id': user.country_id,
                            'state_id': user.state_id,
                            'address_line_1': user.address_line_1,
                            'address_line_2': user.address_line_2,
                            'city_id': user.city_id,
                            'pincode': user.pincode,
                            'status': user.status,
                            #'registered_on': user.created_at.isoformat() if user.created_at else None,
                        }
                        return responseObject, 200
                    else:
                        responseObject = {
                            'status': 'fail',
                            'message': 'User not found.'
                        }
                        return responseObject, 404
                except Exception as e:
                    responseObject = {
                        'status': 'fail',
                        'message': 'Error retrieving user: ' + str(e)
                    }
                    return responseObject, 500
            responseObject = {
                'status': 'fail',
                'message': resp
            }
            return responseObject, 401
        else:
            responseObject = {
                'status': 'fail',
                'message': 'Provide a valid auth token.'
            }
            return responseObject, 401

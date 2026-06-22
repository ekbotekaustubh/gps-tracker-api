from flask import request
from flask_restx import Resource, fields

from src.server import bcrypt, db
from src.server.models import User, BlacklistToken
from src.server import user_ns
from src.server.auth.utility import extract_auth_token


user_model = user_ns.model('User', {
    'id': fields.Integer(description='User ID'),
    'name': fields.String(description='Full name'),
    'email': fields.String(description='Email address'),
    'mobile': fields.String(description='Mobile number'),
    'username': fields.String(description='Username'),
    'branch_id': fields.Integer(description='Branch ID'),
    'role_id': fields.Integer(description='Role ID'),
    'country_id': fields.Integer(description='Country ID'),
    'state_id': fields.Integer(description='State ID'),
    'address_line_1': fields.String(description='Address line 1'),
    'address_line_2': fields.String(description='Address line 2'),
    'city_id': fields.Integer(description='City ID'),
    'pincode': fields.String(description='Pincode'),
    'status': fields.Boolean(description='User status')
})


@user_ns.route('/users/<int:user_id>')
class UsersAPI(Resource):
    @user_ns.doc(security='Bearer Auth')
    @user_ns.response(200, 'Success', user_model)
    @user_ns.response(401, 'Invalid token')
    @user_ns.response(404, 'User not found')
    def get(self, user_id):
        """Get user by user ID"""
        auth_token, responseObject, status_code = extract_auth_token()
        if responseObject:
            return responseObject, status_code

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

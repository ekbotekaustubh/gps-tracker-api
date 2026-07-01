from flask import request
from flask_restx import Resource, fields, Namespace

from src.server import db
from src.server.models import User
from src.server.auth.utility import extract_auth_token

# Create namespace
users_ns = Namespace('users', description='User operations')

user_model = users_ns.model('User', {
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

user_update_model = users_ns.model('UserUpdate', {
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


@users_ns.route('/<int:user_id>')
class UserAPI(Resource):
    @users_ns.doc(security='Bearer Auth')
    @users_ns.response(200, 'Success', user_model)
    @users_ns.response(401, 'Invalid token')
    @users_ns.response(404, 'User not found')
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

    @users_ns.expect(user_update_model)
    @users_ns.doc(security='Bearer Auth')
    @users_ns.response(200, 'User successfully updated')
    @users_ns.response(400, 'Invalid input')
    @users_ns.response(401, 'Invalid token')
    @users_ns.response(404, 'User not found')
    def put(self, user_id):
        """Update user by ID"""
        auth_token, responseObject, status_code = extract_auth_token()
        if responseObject:
            return responseObject, status_code

        resp = User.decode_auth_token(auth_token)
        if isinstance(resp, str):
            responseObject = {
                'status': 'fail',
                'message': resp
            }
            return responseObject, 401

        post_data = request.get_json()
        if not post_data:
            responseObject = {
                'status': 'fail',
                'message': 'No input data provided.'
            }
            return responseObject, 400

        try:
            user = User.query.filter_by(id=user_id).first()
            if not user:
                responseObject = {
                    'status': 'fail',
                    'message': 'User not found.'
                }
                return responseObject, 404

            # Only allow updating fields defined in the update model
            update_fields = [
                'name', 'email', 'mobile', 'username', 'branch_id', 'role_id',
                'country_id', 'state_id', 'address_line_1', 'address_line_2',
                'city_id', 'pincode', 'status'
            ]
            for field in update_fields:
                if field in post_data:
                    setattr(user, field, post_data[field])

            db.session.commit()

            responseObject = {
                'status': 'success',
                'message': 'User updated successfully.',
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
            }
            return responseObject, 200
        except Exception as e:
            db.session.rollback()
            responseObject = {
                'status': 'fail',
                'message': 'Error updating user: ' + str(e)
            }
            return responseObject, 500

    @users_ns.doc(security='Bearer Auth')
    @users_ns.response(200, 'User successfully deleted')
    @users_ns.response(401, 'Invalid token')
    @users_ns.response(404, 'User not found')
    def delete(self, user_id):
        """Delete user by ID"""
        auth_token, responseObject, status_code = extract_auth_token()
        if responseObject:
            return responseObject, status_code

        resp = User.decode_auth_token(auth_token)
        if isinstance(resp, str):
            responseObject = {
                'status': 'fail',
                'message': resp
            }
            return responseObject, 401

        try:
            user = User.query.filter_by(id=user_id).first()
            if not user:
                responseObject = {
                    'status': 'fail',
                    'message': 'User not found.'
                }
                return responseObject, 404

            db.session.delete(user)
            db.session.commit()

            responseObject = {
                'status': 'success',
                'message': 'User deleted successfully.'
            }
            return responseObject, 200
        except Exception as e:
            db.session.rollback()
            responseObject = {
                'status': 'fail',
                'message': 'Error deleting user: ' + str(e)
            }
            return responseObject, 500

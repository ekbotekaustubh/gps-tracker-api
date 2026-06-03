# src/server/auth/views.py

from flask import request
from flask_restx import Resource, fields

from src.server import bcrypt, db
from src.server.models import User, BlacklistToken
from src.server import auth_ns

# Define Swagger models
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

login_model = auth_ns.model('Login', {
    'username': fields.String(required=True, description='Username'),
    'password': fields.String(required=True, description='Password')
})

authorizations = {
    'Bearer Auth': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization',
        'description': 'Enter your bearer token in the format: Bearer <token>'
    }
}

@auth_ns.route('/register')
class RegisterAPI(Resource):
    @auth_ns.expect(register_model)
    @auth_ns.response(201, 'User successfully registered')
    @auth_ns.response(202, 'User already exists')
    @auth_ns.response(401, 'Registration failed')
    def post(self):
        """Register a new user"""
        post_data = request.get_json()
        user = User.query.filter_by(username=post_data.get('username')).first()
        if not user:
            # Also check email uniqueness
            user_by_email = User.query.filter_by(email=post_data.get('email')).first()
            if user_by_email:
                responseObject = {
                    'status': 'fail',
                    'message': 'User with this email already exists. Please Log in.',
                }
                return responseObject, 202
            try:
                user = User(
                    name=post_data.get('name'),
                    email=post_data.get('email'),
                    mobile=post_data.get('mobile'),
                    branch_id=post_data.get('branch_id'),
                    role_id=post_data.get('role_id'),
                    country_id=post_data.get('country_id'),
                    state_id=post_data.get('state_id'),
                    username=post_data.get('username'),
                    password=post_data.get('password'),
                    address_line_1=post_data.get('address_line_1'),
                    address_line_2=post_data.get('address_line_2'),
                    city_id=post_data.get('city_id'),
                    pincode=post_data.get('pincode'),
                )
                db.session.add(user)
                db.session.commit()
                auth_token = user.encode_auth_token(user.id)
                responseObject = {
                    'status': 'success',
                    'message': 'Successfully registered.',
                    'auth_token': auth_token
                }
                return responseObject, 201
            except Exception as e:
                db.session.rollback()
                responseObject = {
                    'status': 'fail',
                    'message': 'Some error occurred: ' + str(e)
                }
                return responseObject, 500
            finally:
                db.session.close()
        else:
            responseObject = {
                'status': 'fail',
                'message': 'User already exists. Please Log in.',
            }
            return responseObject, 202

@auth_ns.route('/login')
class LoginAPI(Resource):
    @auth_ns.expect(login_model)
    @auth_ns.response(200, 'Successfully logged in')
    @auth_ns.response(404, 'User does not exist')
    @auth_ns.response(500, 'Internal server error')
    def post(self):
        """Login user"""
        post_data = request.get_json()
        try:
            user = User.query.filter_by(username=post_data.get('username')).first()
            if user and bcrypt.check_password_hash(user.password, post_data.get('password')):
                auth_token = user.encode_auth_token(user.id)
                if auth_token:
                    responseObject = {
                        'status': 'success',
                        'message': 'Successfully logged in.',
                        'auth_token': auth_token,
                        'user_id': user.id,
                        'username': user.username,
                        'name': user.name,
                        'email': user.email,
                        'role_id': user.role_id,
                        'branch_id': user.branch_id,
                    }
                    return responseObject, 200
            else:
                responseObject = {
                    'status': 'fail',
                    'message': 'User does not exist or invalid credentials.'
                }
                return responseObject, 404
        except Exception as e:
            responseObject = {
                'status': 'fail',
                'message': 'Try again ' + str(e)
            }
            return responseObject, 500

@auth_ns.route('/user')
class UserAPI(Resource):
    @auth_ns.doc(security='Bearer Auth')
    @auth_ns.response(200, 'Success')
    @auth_ns.response(401, 'Invalid token')
    def get(self):
        """Get user information"""
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
                user = User.query.filter_by(id=resp).first()
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
                    'user_status': user.status,
                    'registered_on': user.created_at.isoformat() if user.created_at else None,
                }
                return responseObject, 200
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
        
@auth_ns.route('/logout')
class LogoutAPI(Resource):
    @auth_ns.response(200, 'Successfully logged out')
    @auth_ns.response(401, 'Invalid token')
    @auth_ns.response(403, 'No token provided')
    def post(self):
        """Logout user"""
        auth_header = request.headers.get('Authorization')
        if auth_header:
            auth_token = auth_header.split(" ")[1]
        else:
            auth_token = ''
        if auth_token:
            resp = User.decode_auth_token(auth_token)
            if not isinstance(resp, str):
                blacklist_token = BlacklistToken(token=auth_token)
                try:
                    db.session.add(blacklist_token)
                    db.session.commit()
                    responseObject = {
                        'status': 'success',
                        'message': 'Successfully logged out.'
                    }
                    return responseObject, 200
                except Exception as e:
                    responseObject = {
                        'status': 'fail',
                        'message': e
                    }
                    return responseObject, 200
            else:
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
            return responseObject, 403

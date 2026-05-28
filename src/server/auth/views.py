# project/server/auth/views.py


import traceback
import inspect

from flask import Blueprint, request, make_response, jsonify, g
from flask.views import MethodView
from flask_restx import Resource, fields, Namespace

from src.server import bcrypt, db
from src.server.models import User, BlacklistToken
from src.server import auth_ns

auth_blueprint = Blueprint('auth', __name__)

# Define Swagger models
user_model = auth_ns.model('User', {
    'fname': fields.String(required=True, description='First name'),
    'lname': fields.String(required=True, description='Last name'),
    'email': fields.String(required=True, description='Email address'),
    'password': fields.String(required=True, description='Password')
})

login_model = auth_ns.model('Login', {
    'email': fields.String(required=True, description='Email address'),
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
    @auth_ns.expect(user_model)
    @auth_ns.response(201, 'User successfully registered')
    @auth_ns.response(202, 'User already exists')
    @auth_ns.response(401, 'Registration failed')
    def post(self):
        """Register a new user"""
        post_data = request.get_json()
        user = User.query.filter_by(email=post_data.get('email')).first()
        if not user:
            try:
                user = User(
                    fname=post_data.get('fname'),
                    lname=post_data.get('lname'),
                    email=post_data.get('email'),
                    password=post_data.get('password'),
                    createdBy=None
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
                responseObject = {
                    'status': 'fail',
                    'message': 'Some error occurred. Please try again.'
                }
                return responseObject, 401
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
            user = User.query.filter_by(email=post_data.get('email')).first()
            if user and bcrypt.check_password_hash(user.password, post_data.get('password')):
                auth_token = user.encode_auth_token(user.id)
                if auth_token:
                    responseObject = {
                        'status': 'success',
                        'message': 'Successfully logged in.',
                        'auth_token': auth_token,
                        'username': user.email,
                        'email': user.email,
                        'first_name': "",
                        'last_name': "",
                    }
                    return responseObject, 200
            else:
                responseObject = {
                    'status': 'fail',
                    'message': 'User does not exist.'
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
                auth_token = auth_header.split(" ")[0]
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
                    'email': user.email,
                    'admin': user.admin,
                    'registered_on': user.createOn.isoformat() if user.createOn else None,  
                    'username': user.email,
                    'first_name': "",
                    'last_name': "",
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

# define the API resources
registration_view = RegisterAPI.as_view('register_api')
login_view = LoginAPI.as_view('login_api')
user_view = UserAPI.as_view('user_api')
logout_view = LogoutAPI.as_view('logout_api')

# add Rules for API Endpoints
auth_blueprint.add_url_rule(
    '/auth/register',
    view_func=registration_view,
    methods=['POST']
)
auth_blueprint.add_url_rule(
    '/auth/login',
    view_func=login_view,
    methods=['POST']
)
auth_blueprint.add_url_rule(
    '/auth/user',
    view_func=user_view,
    methods=['GET']
)
auth_blueprint.add_url_rule(
    '/auth/logout',
    view_func=logout_view,
    methods=['POST']
)

auth_blueprint.add_url_rule(
    '/auth/refresh',
    view_func=user_view,
    methods=['GET']
)

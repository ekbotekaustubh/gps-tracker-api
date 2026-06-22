from functools import wraps
from flask import request, make_response, jsonify, g
from src.server.models import User


def extract_auth_token(auth_header=None):
    if auth_header is None:
        auth_header = request.headers.get('Authorization')
    if not auth_header:
        return None, {
            'status': 'fail',
            'message': 'Provide a valid auth token.'
        }, 401

    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != 'bearer':
        return None, {
            'status': 'fail',
            'message': 'Bearer token malformed.'
        }, 401

    return parts[1], None, None


def check_login(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_token, responseObject, status_code = extract_auth_token()
        if responseObject:
            return make_response(jsonify(responseObject)), status_code

        resp = User.decode_auth_token(auth_token)
        if not isinstance(resp, str) and resp is not None:
            user = User.query.filter_by(id=resp).first()
            if user:
                g.user = user  # Store the user in the global context
                return f(*args, **kwargs)
            else:
                responseObject = {
                    'status': 'fail',
                    'message': 'User not found.'
                }
                return make_response(jsonify(responseObject)), 401
        else:
            responseObject = {
                'status': 'fail',
                'message': resp
            }
            return make_response(jsonify(responseObject)), 401

    return decorated_function

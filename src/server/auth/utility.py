from functools import wraps
from flask import Blueprint, request, make_response, jsonify, 
from src.server.models import User

def check_login(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get the auth token
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            responseObject = {
                'status': 'fail',
                'message': 'Provide a valid auth token.'
            }
            return make_response(jsonify(responseObject)), 401

        try:
            auth_token = auth_header.split(" ")[1]
        except IndexError:
            responseObject = {
                'status': 'fail',
                'message': 'Bearer token malformed.'
            }
            return make_response(jsonify(responseObject)), 401

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

# Example usage:
@app.route('/protected', methods=['GET'])
@check_login
def protected():
    return jsonify({'message': 'Hello, {}!'.format(g.user.username)})


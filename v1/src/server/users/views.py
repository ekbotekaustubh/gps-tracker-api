from flask import request
from flask_restx import Resource, fields, Namespace, reqparse

from src.server import db
from src.server.models import User, Branch, Role, Country, State, City
from src.server.auth.utility import extract_auth_token
from src.server.role_permission.utilty import authorize

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
pagination_parser = reqparse.RequestParser()
pagination_parser.add_argument('page', type=int, default=1, help='Page number')
pagination_parser.add_argument('per_page', type=int, default=25, help='Items per page')


@users_ns.route('/<int:user_id>')
class UserAPI(Resource):
    @users_ns.doc(security='Bearer Auth')
    @users_ns.response(200, 'Success', user_model)
    @users_ns.response(401, 'Invalid token')
    @users_ns.response(404, 'User not found')
    @authorize('users.view')  # Example permission key, adjust as needed
    def get(self, user_id):
        """Get user by user ID"""
        auth_token, responseObject, status_code = extract_auth_token()
        if responseObject:
            return responseObject, status_code

        resp = User.decode_auth_token(auth_token)
        if not isinstance(resp, str):
            try:
                user_row = (
                    db.session.query(
                        User,
                        Branch.name.label('branch_name'),
                        Role.name.label('role_name'),
                        Country.name.label('country_name'),
                        State.name.label('state_name'),
                        City.name.label('city_name'),
                    )
                    .outerjoin(Branch, User.branch_id == Branch.id)
                    .outerjoin(Role, User.role_id == Role.id)
                    .outerjoin(Country, User.country_id == Country.id)
                    .outerjoin(State, User.state_id == State.id)
                    .outerjoin(City, User.city_id == City.id)
                    .filter(User.id == user_id)
                    .first()
                )

                if user_row:
                    user, branch_name, role_name, country_name, state_name, city_name = user_row
                    responseObject = {
                        'status': 'success',
                        'user_id': user.id,
                        'name': user.name,
                        'email': user.email,
                        'mobile': user.mobile,
                        'username': user.username,
                        'branch_id': user.branch_id,
                        'branch_name': branch_name,
                        'role_id': user.role_id,
                        'role_name': role_name,
                        'country_id': user.country_id,
                        'country_name': country_name,
                        'state_id': user.state_id,
                        'state_name': state_name,
                        'address_line_1': user.address_line_1,
                        'address_line_2': user.address_line_2,
                        'city_id': user.city_id,
                        'city_name': city_name,
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
    @authorize('users.delete')  # Example permission key, adjust as needed
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
@users_ns.route('/')
class UserListAPI(Resource):

        @users_ns.expect(pagination_parser)
        @users_ns.doc(security='Bearer Auth')
        @users_ns.response(200, 'List of all users')
        @users_ns.response(401, 'Invalid token')
        @authorize('users.view')  # Example permission key, adjust as needed
        def get(self):
            """Get all users"""
            auth_token, responseObject, status_code = extract_auth_token()
            if responseObject:
                return responseObject, status_code
    
            resp = User.decode_auth_token(auth_token)
            if not isinstance(resp, str):
                try:
                    page = request.args.get("page", 1, type=int)
                    per_page = request.args.get("per_page", 25, type=int)

                    pagination = (
                        db.session.query(
                            User,
                            Branch.name.label('branch_name'),
                            Role.name.label('role_name'),
                            Country.name.label('country_name'),
                            State.name.label('state_name'),
                            City.name.label('city_name'),
                        )
                        .outerjoin(Branch, User.branch_id == Branch.id)
                        .outerjoin(Role, User.role_id == Role.id)
                        .outerjoin(Country, User.country_id == Country.id)
                        .outerjoin(State, User.state_id == State.id)
                        .outerjoin(City, User.city_id == City.id)
                        .paginate(page=page, per_page=per_page, error_out=False)
                    )
                    users_list = []

                    for user, branch_name, role_name, country_name, state_name, city_name in pagination.items:
                        users_list.append({
                            'id': user.id,
                            'name': user.name,
                            'email': user.email,
                            'mobile': user.mobile,
                            'username': user.username,
                            'branch_id': user.branch_id,
                            'branch_name': branch_name,
                            'role_id': user.role_id,
                            'role_name': role_name,
                            'country_id': user.country_id,
                            'country_name': country_name,
                            'state_id': user.state_id,
                            'state_name': state_name,
                            'address_line_1': user.address_line_1,
                            'address_line_2': user.address_line_2,
                            'city_id': user.city_id,
                            'city_name': city_name,
                            'status': user.status,
                            'created_at': user.created_at.isoformat() if user.created_at else None,
                            'updated_at': user.updated_at.isoformat() if user.updated_at else None,
                        })
                    
                    responseObject = {
                        'status': 'success',
                        'message': 'Users retrieved successfully',
                        'data': users_list,
                        'total': len(users_list)
                    }
                    return responseObject, 200
                except Exception as e:
                    responseObject = {
                        'status': 'fail',
                        'message': 'Error retrieving users: ' + str(e)
                    }
                    return responseObject, 500
            
            responseObject = {
                'status': 'fail',
                'message': resp
            }
            return responseObject, 401

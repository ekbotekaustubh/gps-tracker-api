from functools import wraps
from flask import request, g
from src.server.models import User, RolePermission, Permission
from src.server.auth.utility import extract_auth_token
from src.server.models.user import User


def authorize(permission_key):
    """
    Example:
    @authorize("permission.create")
    """

    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):

            
            token, error, status = extract_auth_token()

            if error:
                return error, status

            
            user_id = User.decode_auth_token(token)

            if not isinstance(user_id, int):
                return {
                    "status": "fail",
                    "message": user_id
                }, 401

            
            user = User.query.get(user_id)

            if not user:
                return {
                    "status": "fail",
                    "message": "User not found."
                }, 404

            # Save current user
            g.user = user

            # Check Permission
            permission = (
                Permission.query
                .join(RolePermission,
                      Permission.id == RolePermission.permission_id)
                .filter(
                    RolePermission.role_id == user.role_id,
                    Permission.permission_key == permission_key
                )
                .first()
            )

            if not permission:
                return {
                    "status": "fail",
                    "message": "You are not authorized to access this resource."
                }, 403

            return f(*args, **kwargs)

        return wrapper
    return decorator
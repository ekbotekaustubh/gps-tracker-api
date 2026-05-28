# project/server/result/views.py

from flask import Blueprint, request, make_response, jsonify
from flask.views import MethodView
from datetime import datetime, time

from src.server import db
from src.server.models import Result, Profile

result_blueprint = Blueprint('result', __name__)

class ResultAPI(MethodView):
    """
    Result Resource for CRUD operations
    """

    def get(self, result_id=None):
        """
        Read: Get a single result by ID or all results if no ID is provided
        """
        try:
            if result_id:
                # Get a single result
                result = Result.query.get(result_id)
                if not result:
                    return make_response(jsonify({
                        'status': 'fail',
                        'message': 'Result not found.'
                    })), 404

                # Prepare response
                result_data = {
                    'id': result.id,
                    'date': str(result.date),
                    'time': str(result.time),
                    'group': result.group,
                    'test': result.test,
                    'result': result.result,
                    'profile_id': result.profile_id,
                    'profile_name': result.profile.name if result.profile else None,
                    'profile_res': result.profile_res,
                    'printed': result.printed,
                    'y_n': result.y_n,
                    'extra': result.extra
                }
                return make_response(jsonify({
                    'status': 'success',
                    'data': result_data
                })), 200
            else:
                # Get all results
                results = Result.query.all()
                results_data = []
                for result in results:
                    result_data = {
                        'id': result.id,
                        'date': str(result.date),
                        'time': str(result.time),
                        'group': result.group,
                        'test': result.test,
                        'result': result.result,
                        'profile_id': result.profile_id,
                        'profile_name': result.profile.name if result.profile else None,
                        'profile_res': result.profile_res,
                        'printed': result.printed,
                        'y_n': result.y_n,
                        'extra': result.extra
                    }
                    results_data.append(result_data)
                return make_response(jsonify({
                    'status': 'success',
                    'data': results_data
                })), 200
        except Exception as e:
            return make_response(jsonify({
                'status': 'fail',
                'message': f'Error: {str(e)}'
            })), 500

    def post(self):
        """
        Create: Add a new result
        """
        try:
            # Get the post data
            post_data = request.get_json()
            if not post_data:
                return make_response(jsonify({
                    'status': 'fail',
                    'message': 'No data provided.'
                })), 400

            # Parse date and time
            date_str = post_data.get('date')
            time_str = post_data.get('time')
            try:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
                time_obj = datetime.strptime(time_str, '%H:%M:%S').time()
            except ValueError as e:
                return make_response(jsonify({
                    'status': 'fail',
                    'message': f'Invalid date or time format: {str(e)}'
                })), 400

            # Validate profile_id if provided
            profile_id = post_data.get('profile_id')
            if profile_id:
                profile = Profile.query.get(profile_id)
                if not profile:
                    return make_response(jsonify({
                        'status': 'fail',
                        'message': 'Profile not found.'
                    })), 404

            # Create a new result instance
            result = Result(
                id=post_data.get('id'),
                date=date_obj,
                time=time_obj,
                group=post_data.get('group'),
                test=post_data.get('test'),
                result=post_data.get('result'),
                profile_id=profile_id,
                profile_res=post_data.get('profile_res'),
                printed=post_data.get('printed'),
                y_n=post_data.get('y_n'),
                extra=post_data.get('extra')
            )

            # Add the result to the database
            db.session.add(result)
            db.session.commit()

            return make_response(jsonify({
                'status': 'success',
                'message': 'Result created successfully.',
                'result_id': result.id
            })), 201
        except Exception as e:
            db.session.rollback()
            return make_response(jsonify({
                'status': 'fail',
                'message': f'Failed to create result: {str(e)}'
            })), 500

    def put(self, result_id):
        """
        Update: Update an existing result
        """
        try:
            # Find the result
            result = Result.query.get(result_id)
            if not result:
                return make_response(jsonify({
                    'status': 'fail',
                    'message': 'Result not found.'
                })), 404

            # Get the update data
            post_data = request.get_json()
            if not post_data:
                return make_response(jsonify({
                    'status': 'fail',
                    'message': 'No data provided.'
                })), 400

            # Update date and time if provided
            if 'date' in post_data:
                try:
                    result.date = datetime.strptime(post_data['date'], '%Y-%m-%d').date()
                except ValueError as e:
                    return make_response(jsonify({
                        'status': 'fail',
                        'message': f'Invalid date format: {str(e)}'
                    })), 400

            if 'time' in post_data:
                try:
                    result.time = datetime.strptime(post_data['time'], '%H:%M:%S').time()
                except ValueError as e:
                    return make_response(jsonify({
                        'status': 'fail',
                        'message': f'Invalid time format: {str(e)}'
                    })), 400

            # Update profile_id if provided
            if 'profile_id' in post_data:
                profile_id = post_data['profile_id']
                if profile_id:
                    profile = Profile.query.get(profile_id)
                    if not profile:
                        return make_response(jsonify({
                            'status': 'fail',
                            'message': 'Profile not found.'
                        })), 404
                result.profile_id = profile_id

            # Update other fields
            result.group = post_data.get('group', result.group)
            result.test = post_data.get('test', result.test)
            result.result = post_data.get('result', result.result)
            result.profile_res = post_data.get('profile_res', result.profile_res)
            result.printed = post_data.get('printed', result.printed)
            result.y_n = post_data.get('y_n', result.y_n)
            result.extra = post_data.get('extra', result.extra)

            db.session.commit()

            return make_response(jsonify({
                'status': 'success',
                'message': 'Result updated successfully.'
            })), 200
        except Exception as e:
            db.session.rollback()
            return make_response(jsonify({
                'status': 'fail',
                'message': f'Failed to update result: {str(e)}'
            })), 500

    def delete(self, result_id):
        """
        Delete: Delete a result
        """
        try:
            # Find the result
            result = Result.query.get(result_id)
            if not result:
                return make_response(jsonify({
                    'status': 'fail',
                    'message': 'Result not found.'
                })), 404

            # Delete the result
            db.session.delete(result)
            db.session.commit()

            return make_response(jsonify({
                'status': 'success',
                'message': 'Result deleted successfully.'
            })), 200
        except Exception as e:
            db.session.rollback()
            return make_response(jsonify({
                'status': 'fail',
                'message': f'Failed to delete result: {str(e)}'
            })), 500

# Register the API endpoints
result_view = ResultAPI.as_view('result_api')

# Define the API resources
result_blueprint.add_url_rule(
    '/result',
    view_func=result_view,
    methods=['GET', 'POST']  # GET (all results), POST (create)
)

result_blueprint.add_url_rule(
    '/result/<result_id>',
    view_func=result_view,
    methods=['GET', 'PUT', 'DELETE']  # GET (single result), PUT (update), DELETE (delete)
)
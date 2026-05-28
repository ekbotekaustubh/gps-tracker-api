# project/server/consume/views.py

from flask import Blueprint, request, make_response, jsonify
from flask.views import MethodView
from datetime import datetime

from src.server import db
from src.server.models import Consume, Test

consume_blueprint = Blueprint('consume', __name__)

class ConsumeAPI(MethodView):
    """
    Consume Resource for CRUD operations
    """

    def get(self, consume_id=None):
        """
        Read: Get a single consume record by ID or all records if no ID is provided
        """
        try:
            if consume_id:
                # Get a single consume record
                consume = Consume.query.get(consume_id)
                if not consume:
                    return make_response(jsonify({
                        'status': 'fail',
                        'message': 'Consume record not found.'
                    })), 404

                # Prepare response
                consume_data = {
                    'id': consume.id,
                    'date': str(consume.date),
                    'test_id': consume.test_id,
                    'test_name': consume.test.name,
                    'company': consume.company,
                    'no_of_tests_per_day': consume.no_of_tests_per_day
                }
                return make_response(jsonify({
                    'status': 'success',
                    'data': consume_data
                })), 200
            else:
                # Get all consume records
                consumes = Consume.query.all()
                consume_data_list = []
                for consume in consumes:
                    consume_data = {
                        'id': consume.id,
                        'date': str(consume.date),
                        'test_id': consume.test_id,
                        'test_name': consume.test.name,
                        'company': consume.company,
                        'no_of_tests_per_day': consume.no_of_tests_per_day
                    }
                    consume_data_list.append(consume_data)
                return make_response(jsonify({
                    'status': 'success',
                    'data': consume_data_list
                })), 200
        except Exception as e:
            return make_response(jsonify({
                'status': 'fail',
                'message': f'Error: {str(e)}'
            })), 500

    def post(self):
        """
        Create: Add a new consume record
        """
        try:
            # Get the post data
            post_data = request.get_json()
            if not post_data:
                return make_response(jsonify({
                    'status': 'fail',
                    'message': 'No data provided.'
                })), 400

            # Parse date
            date_str = post_data.get('date')
            try:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError as e:
                return make_response(jsonify({
                    'status': 'fail',
                    'message': f'Invalid date format: {str(e)}'
                })), 400

            # Validate test_id
            test_id = post_data.get('test_id')
            test = Test.query.get(test_id)
            if not test:
                return make_response(jsonify({
                    'status': 'fail',
                    'message': 'Test not found.'
                })), 404

            # Create a new consume instance
            consume = Consume(
                date=date_obj,
                test_id=test_id,
                company=post_data.get('company'),
                no_of_tests_per_day=post_data.get('no_of_tests_per_day')
            )

            # Add the consume record to the database
            db.session.add(consume)
            db.session.commit()

            return make_response(jsonify({
                'status': 'success',
                'message': 'Consume record created successfully.',
                'consume_id': consume.id
            })), 201
        except Exception as e:
            db.session.rollback()
            return make_response(jsonify({
                'status': 'fail',
                'message': f'Failed to create consume record: {str(e)}'
            })), 500

    def put(self, consume_id):
        """
        Update: Update an existing consume record
        """
        try:
            # Find the consume record
            consume = Consume.query.get(consume_id)
            if not consume:
                return make_response(jsonify({
                    'status': 'fail',
                    'message': 'Consume record not found.'
                })), 404

            # Get the update data
            post_data = request.get_json()
            if not post_data:
                return make_response(jsonify({
                    'status': 'fail',
                    'message': 'No data provided.'
                })), 400

            # Update date if provided
            if 'date' in post_data:
                try:
                    consume.date = datetime.strptime(post_data['date'], '%Y-%m-%d').date()
                except ValueError as e:
                    return make_response(jsonify({
                        'status': 'fail',
                        'message': f'Invalid date format: {str(e)}'
                    })), 400

            # Update test_id if provided
            if 'test_id' in post_data:
                test_id = post_data['test_id']
                test = Test.query.get(test_id)
                if not test:
                    return make_response(jsonify({
                        'status': 'fail',
                        'message': 'Test not found.'
                    })), 404
                consume.test_id = test_id

            # Update other fields
            consume.company = post_data.get('company', consume.company)
            consume.no_of_tests_per_day = post_data.get('no_of_tests_per_day', consume.no_of_tests_per_day)

            db.session.commit()

            return make_response(jsonify({
                'status': 'success',
                'message': 'Consume record updated successfully.'
            })), 200
        except Exception as e:
            db.session.rollback()
            return make_response(jsonify({
                'status': 'fail',
                'message': f'Failed to update consume record: {str(e)}'
            })), 500

    def delete(self, consume_id):
        """
        Delete: Delete a consume record
        """
        try:
            # Find the consume record
            consume = Consume.query.get(consume_id)
            if not consume:
                return make_response(jsonify({
                    'status': 'fail',
                    'message': 'Consume record not found.'
                })), 404

            # Delete the consume record
            db.session.delete(consume)
            db.session.commit()

            return make_response(jsonify({
                'status': 'success',
                "message": "Consume record deleted successfully."
            })), 200
        except Exception as e:
            db.session.rollback()
            return make_response(jsonify({
                'status': 'fail',
                'message': f'Failed to delete consume record: {str(e)}'
            })), 500

# Register the API endpoints
consume_view = ConsumeAPI.as_view('consume_api')

# Define the API resources
consume_blueprint.add_url_rule(
    '/consume',
    view_func=consume_view,
    methods=['GET', 'POST']  # GET (all consume records), POST (create)
)

consume_blueprint.add_url_rule(
    '/consume/<int:consume_id>',
    view_func=consume_view,
    methods=['GET', 'PUT', 'DELETE']  # GET (single consume record), PUT (update), DELETE (delete)
)
# project/server/today/views.py

from flask import Blueprint, request, make_response, jsonify
from flask.views import MethodView
from datetime import datetime, time

from src.server import db
from src.server.models import Today, Test, today_tests  # Import today_tests

today_blueprint = Blueprint('today', __name__)

class TodayAPI(MethodView):
    """
    Today Resource for CRUD operations
    """

    def get(self, today_id=None):
        """
        Read: Get a single today record by ID or all records if no ID is provided
        """
        try:
            if today_id:
                # Get a single today record
                today = Today.query.get(today_id)
                if not today:
                    return make_response(jsonify({
                        'status': 'fail',
                        'message': 'Today record not found.'
                    })), 404

                # Prepare response with associated tests and results
                today_data = {
                    'id': today.id,
                    'unique_id': today.unique_id,
                    'date': str(today.date),
                    'time': str(today.time),
                    'sr_no': today.sr_no,
                    'name': today.name,
                    'surname': today.surname,
                    'no_of_test': today.no_of_test,
                    'test17_res': today.test17_res,
                    'test18_res': today.test18_res,
                    'test19_res': today.test19_res,
                    'no_of_profile': today.no_of_profile,
                    'workprof': today.workprof,
                    'res': today.res,
                    'tests': [{'test_id': test.id, 'test_name': test.name, 'result': today_tests.c.result} 
                              for test in today.tests]
                }
                return make_response(jsonify({
                    'status': 'success',
                    'data': today_data
                })), 200
            else:
                # Get all today records
                today_records = Today.query.all()
                today_data_list = []
                for today in today_records:
                    today_data = {
                        'id': today.id,
                        'unique_id': today.unique_id,
                        'date': str(today.date),
                        'time': str(today.time),
                        'sr_no': today.sr_no,
                        'name': today.name,
                        'surname': today.surname,
                        'no_of_test': today.no_of_test,
                        'test17_res': today.test17_res,
                        'test18_res': today.test18_res,
                        'test19_res': today.test19_res,
                        'no_of_profile': today.no_of_profile,
                        'workprof': today.workprof,
                        'res': today.res,
                        'tests': [{'test_id': test.id, 'test_name': test.name, 'result': today_tests.c.result} 
                                  for test in today.tests]
                    }
                    today_data_list.append(today_data)
                return make_response(jsonify({
                    'status': 'success',
                    'data': today_data_list
                })), 200
        except Exception as e:
            return make_response(jsonify({
                'status': 'fail',
                'message': f'Error: {str(e)}'
            })), 500

    def post(self):
        """
        Create: Add a new today record
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

            # Create a new today instance
            today = Today(
                unique_id=post_data.get('unique_id'),
                date=date_obj,
                time=time_obj,
                sr_no=post_data.get('sr_no'),
                name=post_data.get('name'),
                surname=post_data.get('surname'),
                no_of_test=post_data.get('no_of_test'),
                test17_res=post_data.get('test17_res'),
                test18_res=post_data.get('test18_res'),
                test19_res=post_data.get('test19_res'),
                no_of_profile=post_data.get('no_of_profile'),
                workprof=post_data.get('workprof'),
                res=post_data.get('res')
            )

            # Add the today record to the database and commit to get the ID
            db.session.add(today)
            db.session.commit()

            # Handle associated tests and results (dynamic test1, res1, test2, res2, ..., testn, resn)
            test_results = post_data.get('test_results', [])  # Expecting a list of {test_id, result}
            if test_results:
                # Fetch the tests
                test_ids = [tr['test_id'] for tr in test_results]
                tests = Test.query.filter(Test.id.in_(test_ids)).all()
                today.tests = tests  # Associate tests with the today record

                # Add results to the junction table
                for tr in test_results:
                    test_id = tr['test_id']
                    result = tr.get('result')
                    db.session.execute(
                        today_tests.insert().values(today_id=today.id, test_id=test_id, result=result)
                    )

            # Commit the changes to the junction table
            db.session.commit()

            return make_response(jsonify({
                'status': 'success',
                'message': 'Today record created successfully.',
                'today_id': today.id
            })), 201
        except Exception as e:
            db.session.rollback()
            return make_response(jsonify({
                'status': 'fail',
                'message': f'Failed to create today record: {str(e)}'
            })), 500

    def put(self, today_id):
        """
        Update: Update an existing today record
        """
        try:
            # Find the today record
            today = Today.query.get(today_id)
            if not today:
                return make_response(jsonify({
                    'status': 'fail',
                    'message': 'Today record not found.'
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
                    today.date = datetime.strptime(post_data['date'], '%Y-%m-%d').date()
                except ValueError as e:
                    return make_response(jsonify({
                        'status': 'fail',
                        'message': f'Invalid date format: {str(e)}'
                    })), 400

            if 'time' in post_data:
                try:
                    today.time = datetime.strptime(post_data['time'], '%H:%M:%S').time()
                except ValueError as e:
                    return make_response(jsonify({
                        'status': 'fail',
                        'message': f'Invalid time format: {str(e)}'
                    })), 400

            # Update other fields
            today.unique_id = post_data.get('unique_id', today.unique_id)
            today.sr_no = post_data.get('sr_no', today.sr_no)
            today.name = post_data.get('name', today.name)
            today.surname = post_data.get('surname', today.surname)
            today.no_of_test = post_data.get('no_of_test', today.no_of_test)
            today.test17_res = post_data.get('test17_res', today.test17_res)
            today.test18_res = post_data.get('test18_res', today.test18_res)
            today.test19_res = post_data.get('test19_res', today.test19_res)
            today.no_of_profile = post_data.get('no_of_profile', today.no_of_profile)
            today.workprof = post_data.get('workprof', today.workprof)
            today.res = post_data.get('res', today.res)

            # Update associated tests and results
            test_results = post_data.get('test_results', None)
            if test_results is not None:
                # Clear existing test associations
                db.session.execute(today_tests.delete().where(today_tests.c.today_id == today.id))
                # Add new test associations
                tests = Test.query.filter(Test.id.in_([tr['test_id'] for tr in test_results])).all()
                today.tests = tests
                for tr in test_results:
                    test_id = tr['test_id']
                    result = tr.get('result')
                    db.session.execute(
                        today_tests.insert().values(today_id=today.id, test_id=test_id, result=result)
                    )

            db.session.commit()

            return make_response(jsonify({
                'status': 'success',
                'message': 'Today record updated successfully.'
            })), 200
        except Exception as e:
            db.session.rollback()
            return make_response(jsonify({
                'status': 'fail',
                'message': f'Failed to update today record: {str(e)}'
            })), 500

    def delete(self, today_id):
        """
        Delete: Delete a today record
        """
        try:
            # Find the today record
            today = Today.query.get(today_id)
            if not today:
                return make_response(jsonify({
                    'status': 'fail',
                    'message': 'Today record not found.'
                })), 404

            # Delete the today record
            db.session.delete(today)
            db.session.commit()

            return make_response(jsonify({
                'status': 'success',
                'message': 'Today record deleted successfully.'
            })), 200
        except Exception as e:
            db.session.rollback()
            return make_response(jsonify({
                'status': 'fail',
                'message': f'Failed to delete today record: {str(e)}'
            })), 500

# Register the API endpoints
today_view = TodayAPI.as_view('today_api')

# Define the API resources
today_blueprint.add_url_rule(
    '/today',
    view_func=today_view,
    methods=['GET', 'POST']  # GET (all today records), POST (create)
)

today_blueprint.add_url_rule(
    '/today/<int:today_id>',
    view_func=today_view,
    methods=['GET', 'PUT', 'DELETE']  # GET (single today record), PUT (update), DELETE (delete)
)
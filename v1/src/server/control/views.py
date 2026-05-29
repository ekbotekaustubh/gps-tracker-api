# project/server/control/views.py

from flask import Blueprint, request, make_response, jsonify
from flask.views import MethodView
from datetime import datetime

from src.server import db
from src.server.models import Control

control_blueprint = Blueprint('control', __name__)

class ControlAPI(MethodView):
    """
    Control Resource for CRUD operations
    """

    def get(self, control_id=None):
        """
        Read: Get a single control by ID or all controls if no ID is provided
        """
        try:
            if control_id:
                # Get a single control
                control = Control.query.get(control_id)
                if not control:
                    return make_response(jsonify({
                        'status': 'fail',
                        'message': 'Control not found.'
                    })), 404

                # Prepare response
                control_data = {
                    'id': control.id,
                    'date': str(control.date),
                    'analyser': control.analyser,
                    'test_name': control.test_name,
                    'control_completed': control.control_completed,
                    'range_low': control.range_low,
                    'low_y_n': control.low_y_n,
                    'range_norm_high': control.range_norm_high,
                    'range_norm_low': control.range_norm_low,
                    'norm_y_n': control.norm_y_n,
                    'range_high': control.range_high,
                    'high_y_n': control.high_y_n
                }
                return make_response(jsonify({
                    'status': 'success',
                    'data': control_data
                })), 200
            else:
                # Get all controls
                controls = Control.query.all()
                controls_data = []
                for control in controls:
                    control_data = {
                        'id': control.id,
                        'date': str(control.date),
                        'analyser': control.analyser,
                        'test_name': control.test_name,
                        'control_completed': control.control_completed,
                        'range_low': control.range_low,
                        'low_y_n': control.low_y_n,
                        'range_norm_high': control.range_norm_high,
                        'range_norm_low': control.range_norm_low,
                        'norm_y_n': control.norm_y_n,
                        'range_high': control.range_high,
                        'high_y_n': control.high_y_n
                    }
                    controls_data.append(control_data)
                return make_response(jsonify({
                    'status': 'success',
                    'data': controls_data
                })), 200
        except Exception as e:
            return make_response(jsonify({
                'status': 'fail',
                'message': f'Error: {str(e)}'
            })), 500

    def post(self):
        """
        Create: Add a new control
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

            # Create a new control instance
            control = Control(
                date=date_obj,
                analyser=post_data.get('analyser'),
                test_name=post_data.get('test_name'),
                control_completed=post_data.get('control_completed'),
                range_low=post_data.get('range_low'),
                low_y_n=post_data.get('low_y_n'),
                range_norm_high=post_data.get('range_norm_high'),
                range_norm_low=post_data.get('range_norm_low'),
                norm_y_n=post_data.get('norm_y_n'),
                range_high=post_data.get('range_high'),
                high_y_n=post_data.get('high_y_n')
            )

            # Add the control to the database
            db.session.add(control)
            db.session.commit()

            return make_response(jsonify({
                'status': 'success',
                'message': 'Control created successfully.',
                'control_id': control.id
            })), 201
        except Exception as e:
            db.session.rollback()
            return make_response(jsonify({
                'status': 'fail',
                'message': f'Failed to create control: {str(e)}'
            })), 500

    def put(self, control_id):
        """
        Update: Update an existing control
        """
        try:
            # Find the control
            control = Control.query.get(control_id)
            if not control:
                return make_response(jsonify({
                    'status': 'fail',
                    'message': 'Control not found.'
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
                    control.date = datetime.strptime(post_data['date'], '%Y-%m-%d').date()
                except ValueError as e:
                    return make_response(jsonify({
                        'status': 'fail',
                        'message': f'Invalid date format: {str(e)}'
                    })), 400

            # Update other fields
            control.analyser = post_data.get('analyser', control.analyser)
            control.test_name = post_data.get('test_name', control.test_name)
            control.control_completed = post_data.get('control_completed', control.control_completed)
            control.range_low = post_data.get('range_low', control.range_low)
            control.low_y_n = post_data.get('low_y_n', control.low_y_n)
            control.range_norm_high = post_data.get('range_norm_high', control.range_norm_high)
            control.range_norm_low = post_data.get('range_norm_low', control.range_norm_low)
            control.norm_y_n = post_data.get('norm_y_n', control.norm_y_n)
            control.range_high = post_data.get('range_high', control.range_high)
            control.high_y_n = post_data.get('high_y_n', control.high_y_n)

            db.session.commit()

            return make_response(jsonify({
                'status': 'success',
                'message': 'Control updated successfully.'
            })), 200
        except Exception as e:
            db.session.rollback()
            return make_response(jsonify({
                'status': 'fail',
                'message': f'Failed to update control: {str(e)}'
            })), 500

    def delete(self, control_id):
        """
        Delete: Delete a control
        """
        try:
            # Find the control
            control = Control.query.get(control_id)
            if not control:
                return make_response(jsonify({
                    'status': 'fail',
                    'message': 'Control not found.'
                })), 404

            # Delete the control
            db.session.delete(control)
            db.session.commit()

            return make_response(jsonify({
                'status': 'success',
                'message': 'Control deleted successfully.'
            })), 200
        except Exception as e:
            db.session.rollback()
            return make_response(jsonify({
                'status': 'fail',
                'message': f'Failed to delete control: {str(e)}'
            })), 500

# Register the API endpoints
control_view = ControlAPI.as_view('control_api')

# Define the API resources
control_blueprint.add_url_rule(
    '/control',
    view_func=control_view,
    methods=['GET', 'POST']  # GET (all controls), POST (create)
)

control_blueprint.add_url_rule(
    '/control/<int:control_id>',
    view_func=control_view,
    methods=['GET', 'PUT', 'DELETE']  # GET (single control), PUT (update), DELETE (delete)
)

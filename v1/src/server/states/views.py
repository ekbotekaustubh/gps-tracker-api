# src/server/states/views.py

from flask_restx import Resource, fields
from src.server import db
from src.server.models import Country, State
from src.server import states_ns
from src.server.role_permission.utilty import authorize


# Define Swagger models
state_model = states_ns.model('State', {
    'id': fields.Integer(description='State ID'),
    'name': fields.String(description='State name'),
    'state_code': fields.String(description='State code'),
    'country_id': fields.Integer(description='Country ID'),
    'created_at': fields.DateTime(description='Created at'),
    'updated_at': fields.DateTime(description='Updated at'),
})


@states_ns.route('/<int:country_id>')
class CountryStatesAPI(Resource):
    @states_ns.response(200, 'Success', [state_model])
    @states_ns.response(404, 'Country not found')
    @states_ns.response(500, 'Internal server error')
    @states_ns.doc(security='Bearer Auth')
    @authorize('state.view')  # Example permission key, adjust as needed
    def get(self, country_id):
        """Get states list of a specific country by country ID"""
        try:
            country = Country.query.filter_by(id=country_id).first()
            if not country:
                return {
                    'status': 'fail',
                    'message': 'Country not found.'
                }, 404

            states = State.query.filter_by(country_id=country_id).all()
            states_list = [
                {
                    'id': state.id,
                    'name': state.name,
                    'state_code': state.state_code,
                    'country_id': state.country_id,
                    'created_at': state.created_at.isoformat() if state.created_at else None,
                    'updated_at': state.updated_at.isoformat() if state.updated_at else None,
                }
                for state in states
            ]
            return {
                'status': 'success',
                'message': 'States retrieved successfully.',
                'data': states_list
            }, 200
        except Exception as e:
            return {
                'status': 'fail',
                'message': f'Error retrieving states: {str(e)}'
            }, 500

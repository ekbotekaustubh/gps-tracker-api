# src/server/cities/views.py

from flask_restx import Resource, fields
from src.server import db
from src.server.models import State, City
from src.server import cities_ns


# Define Swagger models
city_model = cities_ns.model('City', {
    'id': fields.Integer(description='City ID'),
    'name': fields.String(description='City name'),
    'state_id': fields.Integer(description='State ID'),
    'country_id': fields.Integer(description='Country ID'),
    'created_at': fields.DateTime(description='Created at'),
    'updated_at': fields.DateTime(description='Updated at'),
})


@cities_ns.route('/<int:state_id>')
class StateCitiesAPI(Resource):
    @cities_ns.response(200, 'Success', [city_model])
    @cities_ns.response(404, 'State not found')
    @cities_ns.response(500, 'Internal server error')
    def get(self, state_id):
        """Get cities list of a specific state by state ID"""
        try:
            state = State.query.filter_by(id=state_id).first()
            if not state:
                return {
                    'status': 'fail',
                    'message': 'State not found.'
                }, 404

            cities = City.query.filter_by(state_id=state_id).all()
            cities_list = [
                {
                    'id': city.id,
                    'name': city.name,
                    'state_id': city.state_id,
                    'country_id': city.country_id,
                    'created_at': city.created_at.isoformat() if city.created_at else None,
                    'updated_at': city.updated_at.isoformat() if city.updated_at else None,
                }
                for city in cities
            ]
            return {
                'status': 'success',
                'message': 'Cities retrieved successfully.',
                'data': cities_list
            }, 200
        except Exception as e:
            return {
                'status': 'fail',
                'message': f'Error retrieving cities: {str(e)}'
            }, 500

# src/server/countries/views.py

from flask_restx import Resource, fields
from src.server import db
from src.server.models import Country
from src.server import countries_ns
from src.server.role_permission.utilty import authorize


# Define Swagger models
country_model = countries_ns.model('Country', {
    'id': fields.Integer(description='Country ID'),
    'name': fields.String(description='Country name'),
    'country_code': fields.String(description='Country code'),
    'created_at': fields.DateTime(description='Created at'),
    'updated_at': fields.DateTime(description='Updated at'),
})


@countries_ns.route('')
class CountriesAPI(Resource):
    @countries_ns.response(200, 'Success', [country_model])
    @countries_ns.response(500, 'Internal server error')
    @authorize('countries.view')  # Example permission key, adjust as needed
    def get(self):
        """Get list of all countries"""
        try:
            countries = Country.query.all()
            countries_list = [
                {
                    'id': country.id,
                    'name': country.name,
                    'country_code': country.country_code,
                    'created_at': country.created_at.isoformat() if country.created_at else None,
                    'updated_at': country.updated_at.isoformat() if country.updated_at else None,
                }
                for country in countries
            ]
            return {
                'status': 'success',
                'message': 'Countries retrieved successfully.',
                'data': countries_list
            }, 200
        except Exception as e:
            return {
                'status': 'fail',
                'message': f'Error retrieving countries: {str(e)}'
            }, 500


@countries_ns.route('/<int:country_id>')
class CountryDetailAPI(Resource):
    @countries_ns.response(200, 'Success', country_model)
    @countries_ns.response(404, 'Country not found')
    @countries_ns.response(500, 'Internal server error')
    @authorize('countries.view')  # Example permission key, adjust as needed
    def get(self, country_id):
        """Get a specific country by ID"""
        try:
            country = Country.query.filter_by(id=country_id).first()
            if not country:
                return {
                    'status': 'fail',
                    'message': 'Country not found.'
                }, 404

            return {
                'status': 'success',
                'message': 'Country retrieved successfully.',
                'data': {
                    'id': country.id,
                    'name': country.name,
                    'country_code': country.country_code,
                    'created_at': country.created_at.isoformat() if country.created_at else None,
                    'updated_at': country.updated_at.isoformat() if country.updated_at else None,
                }
            }, 200
        except Exception as e:
            return {
                'status': 'fail',
                'message': f'Error retrieving country: {str(e)}'
            }, 500

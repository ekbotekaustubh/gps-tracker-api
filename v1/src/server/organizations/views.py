from flask import request
from flask_restx import Resource, fields

from src.server import db
from src.server import organizations_ns
from src.server.models import Organization


# Swagger Model
organisation_model = organizations_ns.model('Organisation', {
    'id': fields.Integer(description='Organisation ID'),
    'name': fields.String(required=True, description='Organisation Name'),
    'address_line_1': fields.String(required=True, description='Address Line 1'),
    'address_line_2': fields.String(description='Address Line 2'),
    'city': fields.String(required=True, description='City'),
    'pincode': fields.String(required=True, description='Pincode'),
    'country_id': fields.Integer(required=True, description='Country ID'),
    'state_id': fields.Integer(required=True, description='State ID'),
    'status': fields.Boolean(required=True, description='Status'),
    'created_at': fields.DateTime(description='Created At'),
    'updated_at': fields.DateTime(description='Updated At')
})


@organizations_ns.route('')
class organizationsAPI(Resource):

    @organizations_ns.expect(organisation_model)
    @organizations_ns.response(201, 'Organisation created successfully')
    @organizations_ns.response(409, 'Organisation already exists')
    @organizations_ns.response(500, 'Internal server error')
    def post(self):
        """Create Organisation"""

        post_data = request.get_json()

        try:

            organisation = Organization.query.filter_by(
                name=post_data.get('name')
            ).first()

            if organisation:
                responseObject = {
                    'status': 'fail',
                    'message': 'Organisation already exists.'
                }
                return responseObject, 409

            organisation = Organization(
                name=post_data.get('name'),
                address_line_1=post_data.get('address_line_1'),
                address_line_2=post_data.get('address_line_2'),
                city=post_data.get('city'),
                pincode=post_data.get('pincode'),
                country_id=post_data.get('country_id'),
                state_id=post_data.get('state_id'),
                status=post_data.get('status')
            )

            db.session.add(organisation)
            db.session.commit()

            responseObject = {
                'status': 'success',
                'message': 'Organisation added successfully.'
            }

            return responseObject, 201

        except Exception as e:

            db.session.rollback()

            responseObject = {
                'status': 'fail',
                'message': 'Some error occurred: ' + str(e)
            }

            return responseObject, 500

        finally:
            db.session.close()

##########################################################################
    @organizations_ns.response(200, 'Success', [organisation_model])
    @organizations_ns.response(404, 'Organisation not found')
    @organizations_ns.response(500, 'Internal server error')
    def get(self):
        """Get organisation list or organisation by name"""

        organisation_name = request.args.get('name')

        try:

            # GET /api/v1/organizations?name=ABC
            if organisation_name:

                organisation = Organization.query.filter_by(
                    name=organisation_name
                ).first()

                if not organisation:
                    responseObject = {
                        'status': 'fail',
                        'message': 'Organisation not found.'
                    }
                    return responseObject, 404

                responseObject = {
                    'status': 'success',
                    'message': 'Organisation retrieved successfully.',
                    'data': {
                        'id': organisation.id,
                        'name': organisation.name,
                        'address_line_1': organisation.address_line_1,
                        'address_line_2': organisation.address_line_2,
                        'city': organisation.city,
                        'pincode': organisation.pincode,
                        'country_id': organisation.country_id,
                        'state_id': organisation.state_id,
                        'status': organisation.status,
                        'created_at': organisation.created_at.isoformat() if organisation.created_at else None,
                        'updated_at': organisation.updated_at.isoformat() if organisation.updated_at else None,
                    }
                }

                return responseObject, 200

            # GET /api/v1/organizations
            organizations = Organization.query.all()

            organizations_list = [
                {
                    'id': organisation.id,
                    'name': organisation.name,
                    'address_line_1': organisation.address_line_1,
                    'address_line_2': organisation.address_line_2,
                    'city': organisation.city,
                    'pincode': organisation.pincode,
                    'country_id': organisation.country_id,
                    'state_id': organisation.state_id,
                    'status': organisation.status,
                    'created_at': organisation.created_at.isoformat() if organisation.created_at else None,
                    'updated_at': organisation.updated_at.isoformat() if organisation.updated_at else None,
                }
                for organisation in organizations
            ]

            responseObject = {
                'status': 'success',
                'message': 'organizations retrieved successfully.',
                'data': organizations_list
            }

            return responseObject, 200

        except Exception as e:

            responseObject = {
                'status': 'fail',
                'message': 'Error retrieving organizations: ' + str(e)
            }

            return responseObject, 500

 ###########################################################
@organizations_ns.route('/<int:organisation_id>')
class OrganisationAPI(Resource):

    @organizations_ns.response(200, 'Success', organisation_model)
    @organizations_ns.response(404, 'Organisation not found')
    @organizations_ns.response(500, 'Internal server error')
    def get(self, organisation_id):
        """Get organisation details by ID"""

        try:

            organisation = Organization.query.filter_by(
                id=organisation_id
            ).first()

            if not organisation:

                responseObject = {
                    'status': 'fail',
                    'message': 'Organisation not found.'
                }

                return responseObject, 404

            responseObject = {
                'status': 'success',
                'message': 'Organisation retrieved successfully.',
                'data': {
                    'id': organisation.id,
                    'name': organisation.name,
                    'address_line_1': organisation.address_line_1,
                    'address_line_2': organisation.address_line_2,
                    'city': organisation.city,
                    'pincode': organisation.pincode,
                    'country_id': organisation.country_id,
                    'state_id': organisation.state_id,
                    'status': organisation.status,
                    'created_at': organisation.created_at.isoformat() if organisation.created_at else None,
                    'updated_at': organisation.updated_at.isoformat() if organisation.updated_at else None
                }
            }

            return responseObject, 200

        except Exception as e:

            responseObject = {
                'status': 'fail',
                'message': 'Error retrieving organisation: ' + str(e)
            }

            return responseObject, 500

####################################################################
@organizations_ns.route('/<int:organisation_id>')
class OrganisationAPI(Resource):

    @organizations_ns.response(200, 'Success', organisation_model)
    @organizations_ns.response(404, 'Organisation not found')
    @organizations_ns.response(500, 'Internal server error')
    def get(self, organisation_id):
        """Get organisation details by ID"""

        try:

            organisation = Organization.query.filter_by(
                id=organisation_id
            ).first()

            if not organisation:

                responseObject = {
                    'status': 'fail',
                    'message': 'Organisation not found.'
                }

                return responseObject, 404

            responseObject = {
                'status': 'success',
                'message': 'Organisation retrieved successfully.',
                'data': {
                    'id': organisation.id,
                    'name': organisation.name,
                    'address_line_1': organisation.address_line_1,
                    'address_line_2': organisation.address_line_2,
                    'city': organisation.city,
                    'pincode': organisation.pincode,
                    'country_id': organisation.country_id,
                    'state_id': organisation.state_id,
                    'status': organisation.status,
                    'created_at': organisation.created_at.isoformat() if organisation.created_at else None,
                    'updated_at': organisation.updated_at.isoformat() if organisation.updated_at else None
                }
            }

            return responseObject, 200

        except Exception as e:

            responseObject = {
                'status': 'fail',
                'message': 'Error retrieving organisation: ' + str(e)
            }

            return responseObject, 500
#################################################################

    @organizations_ns.expect(organisation_model)
    @organizations_ns.response(200, 'Organisation updated successfully')
    @organizations_ns.response(404, 'Organisation not found')
    @organizations_ns.response(500, 'Internal server error')
    def put(self, organisation_id):
        """Update organisation"""

        post_data = request.get_json()

        try:

            organisation = Organization.query.filter_by(
                id=organisation_id
            ).first()

            if not organisation:

                responseObject = {
                    'status': 'fail',
                    'message': 'Organisation not found.'
                }

                return responseObject, 404

            organisation.name = post_data.get('name', organisation.name)
            organisation.address_line_1 = post_data.get(
                'address_line_1',
                organisation.address_line_1
            )
            organisation.address_line_2 = post_data.get(
                'address_line_2',
                organisation.address_line_2
            )
            organisation.city = post_data.get(
                'city',
                organisation.city
            )
            organisation.pincode = post_data.get(
                'pincode',
                organisation.pincode
            )
            organisation.country_id = post_data.get(
                'country_id',
                organisation.country_id
            )
            organisation.state_id = post_data.get(
                'state_id',
                organisation.state_id
            )
            organisation.status = post_data.get(
                'status',
                organisation.status
            )

            db.session.commit()

            responseObject = {
                'status': 'success',
                'message': 'Organisation updated successfully.'
            }

            return responseObject, 200

        except Exception as e:

            db.session.rollback()

            responseObject = {
                'status': 'fail',
                'message': 'Some error occurred: ' + str(e)
            }

            return responseObject, 500

        finally:

            db.session.close()
########################################################################

    @organizations_ns.response(200, 'Organisation deleted successfully')
    @organizations_ns.response(404, 'Organisation not found')
    @organizations_ns.response(500, 'Internal server error')
    def delete(self, organisation_id):
        """Delete organisation"""

        try:

            organisation = Organization.query.filter_by(
                id=organisation_id
            ).first()

            if not organisation:

                responseObject = {
                    'status': 'fail',
                    'message': 'Organisation not found.'
                }

                return responseObject, 404

            db.session.delete(organisation)
            db.session.commit()

            responseObject = {
                'status': 'success',
                'message': 'Organisation deleted successfully.'
            }

            return responseObject, 200

        except Exception as e:

            db.session.rollback()

            responseObject = {
                'status': 'fail',
                'message': 'Some error occurred: ' + str(e)
            }

            return responseObject, 500

        finally:

            db.session.close()
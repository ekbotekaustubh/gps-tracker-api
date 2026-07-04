from flask import request
from flask_restx import Resource, fields

from src.server import db
from src.server import organizations_ns
from src.server.models import Organization


# Swagger Model
organization_model = organizations_ns.model('Organization', {
    'id': fields.Integer(description='Organization ID'),
    'name': fields.String(required=True, description='Organization Name'),
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
class OrganizationsListAPI(Resource):
    """Collection endpoint: POST (create) and GET (list or query by name)"""

    @organizations_ns.expect(organization_model)
    @organizations_ns.response(201, 'Organization created successfully')
    @organizations_ns.response(409, 'Organization already exists')
    @organizations_ns.response(500, 'Internal server error')
    def post(self):
        """Create Organization"""

        post_data = request.get_json()

        try:
            organization = Organization.query.filter_by(
                name=post_data.get('name')
            ).first()

            if organization:
                responseObject = {
                    'status': 'fail',
                    'message': 'Organization already exists.'
                }
                return responseObject, 409

            organization = Organization(
                name=post_data.get('name'),
                address_line_1=post_data.get('address_line_1'),
                address_line_2=post_data.get('address_line_2'),
                city=post_data.get('city'),
                pincode=post_data.get('pincode'),
                country_id=post_data.get('country_id'),
                state_id=post_data.get('state_id'),
                status=post_data.get('status')
            )

            db.session.add(organization)
            db.session.commit()

            responseObject = {
                'status': 'success',
                'message': 'Organization added successfully.',
                'data': {'id': organization.id}
            }

            return responseObject, 201

        except Exception as e:
            db.session.rollback()
            responseObject = {'status': 'fail', 'message': 'Some error occurred: ' + str(e)}
            return responseObject, 500
        finally:
            db.session.close()

    @organizations_ns.response(200, 'Success', [organization_model])
    @organizations_ns.response(500, 'Internal server error')
    def get(self):
        """Get organization list or organization by name (query param 'name')"""

        try:
            organization_name = request.args.get('name')
            if organization_name:
                organization = Organization.query.filter_by(name=organization_name).first()
                if not organization:
                    return {'status': 'fail', 'message': 'Organization not found.'}, 404

                return {
                    'status': 'success',
                    'message': 'organization retrieved successfully.',
                    'data': {
                        'id': organization.id,
                        'name': organization.name,
                        'address_line_1': organization.address_line_1,
                        'address_line_2': organization.address_line_2,
                        'city': organization.city,
                        'pincode': organization.pincode,
                        'country_id': organization.country_id,
                        'state_id': organization.state_id,
                        'status': organization.status,
                        'created_at': organization.created_at.isoformat() if organization.created_at else None,
                        'updated_at': organization.updated_at.isoformat() if organization.updated_at else None,
                    }
                }, 200

            organizations = Organization.query.all()
            organizations_list = [
                {
                    'id': org.id,
                    'name': org.name,
                    'address_line_1': org.address_line_1,
                    'address_line_2': org.address_line_2,
                    'city': org.city,
                    'pincode': org.pincode,
                    'country_id': org.country_id,
                    'state_id': org.state_id,
                    'status': org.status,
                    'created_at': org.created_at.isoformat() if org.created_at else None,
                    'updated_at': org.updated_at.isoformat() if org.updated_at else None,
                }
                for org in organizations
            ]

            return {'status': 'success', 'message': 'organizations retrieved successfully.', 'data': organizations_list}, 200

        except Exception as e:
            return {'status': 'fail', 'message': 'Error retrieving organizations: ' + str(e)}, 500


@organizations_ns.route('/<int:organization_id>')
class OrganizationAPI(Resource):
    """Item endpoint: GET, PUT, DELETE for a single organization"""

    @organizations_ns.response(200, 'Success', organization_model)
    @organizations_ns.response(404, 'organization not found')
    @organizations_ns.response(500, 'Internal server error')
    def get(self, organization_id):
        """Get organization details by ID"""
        try:
            organization = Organization.query.filter_by(id=organization_id).first()
            if not organization:
                return {'status': 'fail', 'message': 'organization not found.'}, 404

            return {
                'status': 'success',
                'message': 'organization retrieved successfully.',
                'data': {
                    'id': organization.id,
                    'name': organization.name,
                    'address_line_1': organization.address_line_1,
                    'address_line_2': organization.address_line_2,
                    'city': organization.city,
                    'pincode': organization.pincode,
                    'country_id': organization.country_id,
                    'state_id': organization.state_id,
                    'status': organization.status,
                    'created_at': organization.created_at.isoformat() if organization.created_at else None,
                    'updated_at': organization.updated_at.isoformat() if organization.updated_at else None
                }
            }, 200

        except Exception as e:
            return {'status': 'fail', 'message': 'Error retrieving organization: ' + str(e)}, 500

    @organizations_ns.expect(organization_model)
    @organizations_ns.response(200, 'organization updated successfully')
    @organizations_ns.response(404, 'organization not found')
    @organizations_ns.response(500, 'Internal server error')
    def put(self, organization_id):
        """Update organization"""
        post_data = request.get_json()
        try:
            organization = Organization.query.filter_by(id=organization_id).first()
            if not organization:
                return {'status': 'fail', 'message': 'organization not found.'}, 404

            organization.name = post_data.get('name', organization.name)
            organization.address_line_1 = post_data.get('address_line_1', organization.address_line_1)
            organization.address_line_2 = post_data.get('address_line_2', organization.address_line_2)
            organization.city = post_data.get('city', organization.city)
            organization.pincode = post_data.get('pincode', organization.pincode)
            organization.country_id = post_data.get('country_id', organization.country_id)
            organization.state_id = post_data.get('state_id', organization.state_id)
            organization.status = post_data.get('status', organization.status)

            db.session.commit()
            return {'status': 'success', 'message': 'organization updated successfully.'}, 200

        except Exception as e:
            db.session.rollback()
            return {'status': 'fail', 'message': 'Some error occurred: ' + str(e)}, 500
        finally:
            db.session.close()

    @organizations_ns.response(200, 'organization deleted successfully')
    @organizations_ns.response(404, 'organization not found')
    @organizations_ns.response(500, 'Internal server error')
    def delete(self, organization_id):
        """Delete organization"""
        try:
            organization = Organization.query.filter_by(id=organization_id).first()
            if not organization:
                return {'status': 'fail', 'message': 'organization not found.'}, 404

            db.session.delete(organization)
            db.session.commit()
            return {'status': 'success', 'message': 'organization deleted successfully.'}, 200

        except Exception as e:
            db.session.rollback()
            return {'status': 'fail', 'message': 'Some error occurred: ' + str(e)}, 500
        finally:
            db.session.close()

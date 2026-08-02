from flask import request
from flask_restx import Resource, fields, Namespace

from src.server import db
from src.server.models import Branch, Organization, Country, State, City
from src.server.role_permission.utilty import authorize
from src.server.auth.utility import extract_auth_token
#from src.server import branchs_ns


branchs_ns = Namespace('branchs', description='Branch operations')



branch_response_model = branchs_ns.model('Branch', {
    'id': fields.Integer(description='Branch ID'),
    'org_id': fields.Integer(description='Organization ID'),
    'name': fields.String(description='Branch name'),
    'address_line_1': fields.String(description='Address line 1'),
    'address_line_2': fields.String(description='Address line 2'),
    'city': fields.String(description='City'),
    'pincode': fields.String(description='Pincode'),
    'country_id': fields.Integer(description='Country ID'),
    'state_id': fields.Integer(description='State ID'),
    'city_id': fields.Integer(description='City ID'),
    'is_head_office': fields.Integer(description='Is head office'),
    'mobile': fields.String(description='Mobile number'),
    'phone': fields.String(description='Phone number'),
    'status': fields.Integer(description='Branch status'),
    'created_at': fields.String(description='Created at'),
    'updated_at': fields.String(description='Updated at'),
})

branch_input_model = branchs_ns.model('BranchInput', {
    'org_id': fields.Integer(required=True, description='Organization ID'),
    'name': fields.String(required=True, description='Branch name'),
    'address_line_1': fields.String(required=True, description='Address line 1'),
    'address_line_2': fields.String(required=False, description='Address line 2'),
    'city': fields.String(required=True, description='City'),
    'pincode': fields.String(required=True, description='Pincode'),
    'country_id': fields.Integer(required=True, description='Country ID'),
    'state_id': fields.Integer(required=True, description='State ID'),
    'city_id': fields.Integer(required=False, description='City ID'),
    'is_head_office': fields.Integer(required=False, description='Is head office'),
    'mobile': fields.String(required=True, description='Mobile number'),
    'phone': fields.String(required=False, description='Phone number'),
    'status': fields.Integer(required=False, description='Branch status'),
})


def serialize_branch(branch, org_name=None, country_name=None, state_name=None, city_name=None):
    return {
        'id': branch.id,
        'org_id': branch.org_id,
        'org_name': org_name,
        'name': branch.name,
        'address_line_1': branch.address_line_1,
        'address_line_2': branch.address_line_2,
        'city': branch.city,
        'pincode': branch.pincode,
        'country_id': branch.country_id,
        'country_name': country_name,
        'state_id': branch.state_id,
        'state_name': state_name,
        'city_id': branch.city_id,
        'city_name': city_name,
        'is_head_office': branch.is_head_office,
        'mobile': branch.mobile,
        'phone': branch.phone,
        'status': branch.status,
        'created_at': branch.created_at.isoformat() if branch.created_at else None,
        'updated_at': branch.updated_at.isoformat() if branch.updated_at else None,
    }


@branchs_ns.route('/')
class AddBranchAPI(Resource):
    @branchs_ns.expect(branch_input_model)
    @branchs_ns.response(201, 'Branch added successfully', branch_response_model)
    @branchs_ns.response(400, 'Invalid input')
    @authorize('branches.create') 
    @branchs_ns.doc(security='Bearer Auth') # Example permission key, adjust as needed
    def post(self):
        """Add a new branch"""
        auth_token, responseObject, status_code = extract_auth_token()
        if responseObject:
            return responseObject, status_code
            try:
                data = request.get_json()
            
            
                required_data = ['org_id', 'name', 'address_line_1', 'city', 'pincode', 'country_id', 'state_id', 'mobile']
                for field in required_data:
                    if field not in data or not data[field]:
                        responseObject = {
                            'status': 'fail',
                            'message': f'Missing required field: {field}'
                        }
                        return responseObject, 400
            
            
                branch = Branch(
                    org_id=data['org_id'],
                    name=data['name'],
                    address_line_1=data['address_line_1'],
                    address_line_2=data.get('address_line_2', ''),
                    city=data['city'],
                    pincode=data['pincode'],
                    country_id=data['country_id'],
                    state_id=data['state_id'],
                    city_id=data.get('city_id'),
                    is_head_office=data.get('is_head_office', 0),
                    mobile=data['mobile'],
                    phone=data.get('phone', ''),
                    status=data.get('status', 1)
                )
            
                db.session.add(branch)
                db.session.commit()
            
                responseObject = {
                    'status': 'success',
                    'message': 'Branch added successfully',
                    'data': {
                        'id': branch.id,
                        'org_id': branch.org_id,
                        'name': branch.name,
                        'address_line_1': branch.address_line_1,
                        'address_line_2': branch.address_line_2,
                        'city': branch.city,
                        'pincode': branch.pincode,
                        'country_id': branch.country_id,
                        'state_id': branch.state_id,
                        'city_id': branch.city_id,
                        'is_head_office': branch.is_head_office,
                        'mobile': branch.mobile,
                        'phone': branch.phone,
                        'status': branch.status,
                        'created_at': str(branch.created_at),
                        'updated_at': str(branch.updated_at),
                    }
                }
                return responseObject, 201
            except Exception as e:
                db.session.rollback()
                responseObject = {
                    'status': 'fail',
                    'message': str(e)
                }
                return responseObject, 400


    @branchs_ns.response(200, 'Success')
    @authorize('branches.view') 
    @branchs_ns.doc(security='Bearer Auth') # Example permission key, adjust as needed
    def get(self):
        """Get all branches"""
        try:
            branches = (
                db.session.query(
                    Branch,
                    Organization.name.label('org_name'),
                    Country.name.label('country_name'),
                    State.name.label('state_name'),
                    City.name.label('city_name')
                )
                .outerjoin(Organization, Branch.org_id == Organization.id)
                .outerjoin(Country, Branch.country_id == Country.id)
                .outerjoin(State, Branch.state_id == State.id)
                .outerjoin(City, Branch.city_id == City.id)
                .all()
            )

            branches_list = [
                serialize_branch(branch, org_name, country_name, state_name, city_name)
                for branch, org_name, country_name, state_name, city_name in branches
            ]

            return {
                'status': 'success',
                'message': 'Branches retrieved successfully.',
                'data': branches_list
            }, 200
        except Exception as e:
            return {
                'status': 'fail',
                'message': f'Error retrieving branches: {str(e)}'
            }, 500

      # Example permission key, adjust as needed

 # Example permission key, adjust as needed
@branchs_ns.route('/<int:branch_id>')
class BranchDetailAPI(Resource):
    @branchs_ns.doc(security='Bearer Auth') 
    @branchs_ns.response(200, 'Success')
    @branchs_ns.response(404, 'Branch not found')
    @authorize('branches.view')  # Example permission key, adjust as needed
    def get(self, branch_id):
        """Get a branch by ID"""
        try:
            branch_row = (
                db.session.query(
                    Branch,
                    Organization.name.label('org_name'),
                    Country.name.label('country_name'),
                    State.name.label('state_name'),
                    City.name.label('city_name')
                )
                .outerjoin(Organization, Branch.org_id == Organization.id)
                .outerjoin(Country, Branch.country_id == Country.id)
                .outerjoin(State, Branch.state_id == State.id)
                .outerjoin(City, Branch.city_id == City.id)
                .filter(Branch.id == branch_id)
                .first()
            )

            if not branch_row:
                return {
                    'status': 'fail',
                    'message': 'Branch not found.'
                }, 404

            branch, org_name, country_name, state_name, city_name = branch_row
            return {
                'status': 'success',
                'message': 'Branch retrieved successfully.',
                'data': serialize_branch(branch, org_name, country_name, state_name, city_name)
            }, 200
        except Exception as e:
            return {
                'status': 'fail',
                'message': f'Error retrieving branch: {str(e)}'
            }, 500

    @branchs_ns.expect(branch_input_model)
    @branchs_ns.doc(security='Bearer Auth') 
    @branchs_ns.response(200, 'Branch updated successfully')
    @branchs_ns.response(400, 'Invalid input')
    @branchs_ns.response(404, 'Branch not found')
    @authorize('branches.update')  # Example permission key, adjust as needed
    def put(self, branch_id):
        """Update branch """
        try:
            data = request.get_json()
            if not data:
                return {
                    'status': 'fail',
                    'message': 'No input data provided'
                }, 400

            branch = Branch.query.filter_by(id=branch_id).first()
            if not branch:
                return {
                    'status': 'fail',
                    'message': 'Branch not found.'
                }, 404

            for field in ['org_id', 'name', 'address_line_1', 'city', 'pincode', 'country_id', 'state_id', 'mobile']:
                if field in data and not data[field]:
                    return {
                        'status': 'fail',
                        'message': f'Missing required field: {field}'
                    }, 400

            branch.org_id = data.get('org_id', branch.org_id)
            branch.name = data.get('name', branch.name)
            branch.address_line_1 = data.get('address_line_1', branch.address_line_1)
            branch.address_line_2 = data.get('address_line_2', branch.address_line_2)
            branch.city = data.get('city', branch.city)
            branch.pincode = data.get('pincode', branch.pincode)
            branch.country_id = data.get('country_id', branch.country_id)
            branch.state_id = data.get('state_id', branch.state_id)
            branch.city_id = data.get('city_id', branch.city_id)
            branch.is_head_office = data.get('is_head_office', branch.is_head_office)
            branch.mobile = data.get('mobile', branch.mobile)
            branch.phone = data.get('phone', branch.phone)
            branch.status = data.get('status', branch.status)

            db.session.commit()

            branch_row = (
                db.session.query(
                    Branch,
                    Organization.name.label('org_name'),
                    Country.name.label('country_name'),
                    State.name.label('state_name'),
                    City.name.label('city_name')
                )
                .outerjoin(Organization, Branch.org_id == Organization.id)
                .outerjoin(Country, Branch.country_id == Country.id)
                .outerjoin(State, Branch.state_id == State.id)
                .outerjoin(City, Branch.city_id == City.id)
                .filter(Branch.id == branch.id)
                .first()
            )
            branch_data, org_name, country_name, state_name, city_name = branch_row

            return {
                'status': 'success',
                'message': 'Branch updated successfully.',
                'data': serialize_branch(branch_data, org_name, country_name, state_name, city_name)
            }, 200
        except Exception as e:
            db.session.rollback()
            return {
                'status': 'fail',
                'message': f'Error updating branch: {str(e)}'
            }, 400
    @branchs_ns.doc(security='Bearer Auth') 
    @branchs_ns.response(200, 'Branch deleted successfully')
    @branchs_ns.response(404, 'Branch not found')
    @authorize('branches.delete')  # Example permission key, adjust as needed
    def delete(self, branch_id):
        """Delete branch"""
        try:
            branch = Branch.query.filter_by(id=branch_id).first()
            if not branch:
                return {
                    'status': 'fail',
                    'message': 'Branch not found.'
                }, 404

            db.session.delete(branch)
            db.session.commit()

            return {
                'status': 'success',
                'message': 'Branch deleted successfully.'
            }, 200
        except Exception as e:
            db.session.rollback()
            return {
                'status': 'fail',
                'message': f'Error deleting branch: {str(e)}'
            }, 400

from flask import request
from flask_restx import Resource, fields, Namespace

from src.server import db
from src.server.models import Branch
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


@branchs_ns.route('/')
class AddBranchAPI(Resource):
    @branchs_ns.expect(branch_input_model)
    @branchs_ns.response(201, 'Branch added successfully', branch_response_model)
    @branchs_ns.response(400, 'Invalid input')
    def post(self):
        """Add a new branch"""
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

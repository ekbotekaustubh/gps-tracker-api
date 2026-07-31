from flask import request
from flask_restx import Resource, fields, Namespace

from src.server import db
from src.server.models import CardMember, Branch, Organization, Country, State, City
import traceback
from src.server.role_permission.utilty import authorize

CardMembers_ns = Namespace('card_members', description='Card Members operations')

# Input model for creating/updating card member
card_member_input_model = CardMembers_ns.model('CardMemberInput', {
    'name': fields.String(required=True, description='Card member name'),
    'email': fields.String(description='Email address'),
    'mobile': fields.String(required=True, description='Mobile number'),
    'branch_id': fields.Integer(required=True, description='Branch ID'),
    'address_line_1': fields.String(description='Address line 1'),
    'address_line_2': fields.String(description='Address line 2'),
    'city': fields.String(description='City'),
    'pincode': fields.String(description='Pincode'),
    'country_id': fields.Integer(required=True, description='Country ID'),
    'state_id': fields.Integer(required=True, description='State ID'),
    'city_id': fields.Integer(description='City ID'),
    'card_id': fields.Integer(description='Card ID'),
    'emergency_contact_1': fields.String(required=True, description='Emergency contact 1'),
    'emergency_contact_2': fields.String(description='Emergency contact 2'),
    'emergency_contact_3': fields.String(description='Emergency contact 3'),
    'status': fields.Integer(description='Status (0=inactive, 1=active)', default=1)
})

# Response model for card member
card_member_response_model = CardMembers_ns.model('CardMemberResponse', {
    'id': fields.Integer(description='Card Member ID'),
    'name': fields.String(description='Card member name'),
    'email': fields.String(description='Email address'),
    'mobile': fields.String(description='Mobile number'),
    'branch_id': fields.Integer(description='Branch ID'),
    'branch_name': fields.String(description='Branch name'),
    'address_line_1': fields.String(description='Address line 1'),
    'address_line_2': fields.String(description='Address line 2'),
    'city': fields.String(description='City'),
    'pincode': fields.String(description='Pincode'),
    'country_id': fields.Integer(description='Country ID'),
    'country_name': fields.String(description='Country name'),
    'state_id': fields.Integer(description='State ID'),
    'state_name': fields.String(description='State name'),
    'city_id': fields.Integer(description='City ID'),
    'city_name': fields.String(description='City name'),
    'card_id': fields.Integer(description='Card ID'),
    'emergency_contact_1': fields.String(description='Emergency contact 1'),
    'emergency_contact_2': fields.String(description='Emergency contact 2'),
    'emergency_contact_3': fields.String(description='Emergency contact 3'),
    'status': fields.Integer(description='Status'),
    'created_at': fields.String(description='Created at'),
    'updated_at': fields.String(description='Updated at')
})


def serialize_card_member(member, branch_name=None, country_name=None, state_name=None, city_name=None):
    """Serialize card member to dictionary"""
    return {
        'id': member.id,
        'name': member.name,
        'email': member.email,
        'mobile': member.mobile,
        'branch_id': member.branch_id,
        'branch_name': branch_name,
        'address_line_1': member.address_line_1,
        'address_line_2': member.address_line_2,
        'city': member.city,
        'pincode': member.pincode,
        #'country_id': member.country_id,
        'country_name': country_name,
        #'state_id': member.state_id,
        'state_name': state_name,
        #'city_id': member.city_id,
        'city_name': city_name,
        'card_id': member.card_id,
        'emergency_contact_1': member.emergency_contact_1,
        'emergency_contact_2': member.emergency_contact_2,
        'emergency_contact_3': member.emergency_contact_3,
        'status': member.status,
        'created_at': member.created_at.isoformat() if member.created_at else None,
        'updated_at': member.updated_at.isoformat() if member.updated_at else None,
    }


@CardMembers_ns.route('/')
class CardMemberListAPI(Resource):
    @CardMembers_ns.expect(card_member_input_model)
    @CardMembers_ns.response(201, 'Card member created successfully', card_member_response_model)
    @CardMembers_ns.response(400, 'Invalid input')
    @CardMembers_ns.response(404, 'Branch, Country, State or City not found')
    @authorize('card_members.create')  # Example permission key, adjust as needed
    def post(self):
        """Add a new card member"""
        try:
            data = request.get_json()
            
            if not data:
                return {
                    'status': 'fail',
                    'message': 'No JSON data provided'
                }, 400
            
            # Validate required fields
            required_fields = ['name', 'mobile', 'branch_id', 'country_id', 'state_id', 'emergency_contact_1', 'card_id']
            for field in required_fields:
                if field not in data or not data[field]:
                    return {
                        'status': 'fail',
                        'message': f'Missing required field: {field}'
                    }, 400
            
            # Validate branch exists
            branch = Branch.query.get(data['branch_id'])
            if not branch:
                return {
                    'status': 'fail',
                    'message': f'Branch with ID {data["branch_id"]} not found'
                }, 404
            
            # Validate country exists
            country = Country.query.get(data['country_id'])
            if not country:
                return {
                    'status': 'fail',
                    'message': f'Country with ID {data["country_id"]} not found'
                }, 404
            
            # Validate state exists
            state = State.query.get(data['state_id'])
            if not state:
                return {
                    'status': 'fail',
                    'message': f'State with ID {data["state_id"]} not found'
                }, 404
            
            # Validate city if provided
            city = None
            if data.get('city_id'):
                city = City.query.get(data['city_id'])
                if not city:
                    return {
                        'status': 'fail',
                        'message': f'City with ID {data["city_id"]} not found'
                    }, 404
            
            # Create new card member
            card_member = CardMember(
                name=data['name'],
                email=data.get('email'),
                mobile=data['mobile'],
                branch_id=data['branch_id'],
                address_line_1=data.get('address_line_1'),
                address_line_2=data.get('address_line_2'),
                city=data.get('city'),
                pincode=data.get('pincode'),
                country_id=data['country_id'],
                state_id=data['state_id'],
                city_id=data.get('city_id'),
                card_id=data.get('card_id'),
                emergency_contact_1=data['emergency_contact_1'],
                emergency_contact_2=data.get('emergency_contact_2'),
                emergency_contact_3=data.get('emergency_contact_3'),
                status=data.get('status', 1)
            )
            
            db.session.add(card_member)
            db.session.commit()
            
            return {
                'status': 'success',
                'message': 'Card member created successfully',
                'data': serialize_card_member(
                    card_member,
                    branch_name=branch.name,
                    country_name=country.name,
                    state_name=state.name,
                    city_name=city.name if city else None
                )
            }, 201
            
        except Exception as e:
            db.session.rollback()
            print(f"Error creating card member: {traceback.format_exc()}")
            return {
                'status': 'fail',
                'message': f'Error creating card member: {str(e)}'
            }, 500

    @CardMembers_ns.response(200, 'List of all card members')
    @authorize('card_members.view')  # Example permission key, adjust as needed
    def get(self):
        """Get all card members"""
        try:
            card_members = CardMember.query.all()
            
            result = []
            for member in card_members:
                branch = Branch.query.get(member.branch_id)
                country = Country.query.get(member.country_id)
                state = State.query.get(member.state_id)
                city = City.query.get(member.city_id) if member.city_id else None
                
                result.append(serialize_card_member(
                    member,
                    branch_name=branch.name if branch else None,
                    country_name=country.name if country else None,
                    state_name=state.name if state else None,
                    city_name=city.name if city else None
                ))
            
            return {
                'status': 'success',
                'message': 'Card members retrieved successfully',
                'data': result,
                'total': len(result)
            }, 200
            
        except Exception as e:
            print(f"Error retrieving card members: {traceback.format_exc()}")
            return {
                'status': 'fail',
                'message': f'Error retrieving card members: {str(e)}'
            }, 500


@CardMembers_ns.route('/<int:member_id>')
class CardMemberAPI(Resource):
    @CardMembers_ns.response(200, 'Card member details', card_member_response_model)
    @CardMembers_ns.response(404, 'Card member not found')
    @authorize('card_members.view')  # Example permission key, adjust as needed
    def get(self, member_id):
        """Get a specific card member by ID"""
        try:
            card_member = CardMember.query.get(member_id)
            
            if not card_member:
                return {
                    'status': 'fail',
                    'message': f'Card member with ID {member_id} not found'
                }, 404
            
            branch = Branch.query.get(card_member.branch_id)
            country = Country.query.get(card_member.country_id)
            state = State.query.get(card_member.state_id)
            city = City.query.get(card_member.city_id) if card_member.city_id else None
            
            return {
                'status': 'success',
                'message': 'Card member retrieved successfully',
                'data': serialize_card_member(
                    card_member,
                    branch_name=branch.name if branch else None,
                    country_name=country.name if country else None,
                    state_name=state.name if state else None,
                    city_name=city.name if city else None
                )
            }, 200
            
        except Exception as e:
            print(f"Error retrieving card member: {traceback.format_exc()}")
            return {
                'status': 'fail',
                'message': f'Error retrieving card member: {str(e)}'
            }, 500

    @CardMembers_ns.expect(card_member_input_model)
    @CardMembers_ns.response(200, 'Card member updated successfully', card_member_response_model)
    @CardMembers_ns.response(404, 'Card member not found')
    @CardMembers_ns.response(400, 'Invalid input')
    @authorize('card_members.update')  # Example permission key, adjust as needed
    def put(self, member_id):
        """Update a card member"""
        try:
            card_member = CardMember.query.get(member_id)
            
            if not card_member:
                return {
                    'status': 'fail',
                    'message': f'Card member with ID {member_id} not found'
                }, 404
            
            data = request.get_json()
            
            if not data:
                return {
                    'status': 'fail',
                    'message': 'No JSON data provided'
                }, 400
            
            # Validate foreign keys if provided
            if 'branch_id' in data:
                branch = Branch.query.get(data['branch_id'])
                if not branch:
                    return {
                        'status': 'fail',
                        'message': f'Branch with ID {data["branch_id"]} not found'
                    }, 404
                card_member.branch_id = data['branch_id']
            
            if 'country_id' in data:
                country = Country.query.get(data['country_id'])
                if not country:
                    return {
                        'status': 'fail',
                        'message': f'Country with ID {data["country_id"]} not found'
                    }, 404
                card_member.country_id = data['country_id']
            
            if 'state_id' in data:
                state = State.query.get(data['state_id'])
                if not state:
                    return {
                        'status': 'fail',
                        'message': f'State with ID {data["state_id"]} not found'
                    }, 404
                card_member.state_id = data['state_id']
            
            if 'city_id' in data and data['city_id']:
                city = City.query.get(data['city_id'])
                if not city:
                    return {
                        'status': 'fail',
                        'message': f'City with ID {data["city_id"]} not found'
                    }, 404
                card_member.city_id = data['city_id']
            
            # Update other fields
            if 'name' in data:
                card_member.name = data['name']
            if 'email' in data:
                card_member.email = data['email']
            if 'mobile' in data:
                card_member.mobile = data['mobile']
            if 'address_line_1' in data:
                card_member.address_line_1 = data['address_line_1']
            if 'address_line_2' in data:
                card_member.address_line_2 = data['address_line_2']
            if 'city' in data:
                card_member.city = data['city']
            if 'pincode' in data:
                card_member.pincode = data['pincode']
            if 'card_id' in data:
                card_member.card_id = data['card_id']
            if 'emergency_contact_1' in data:
                card_member.emergency_contact_1 = data['emergency_contact_1']
            if 'emergency_contact_2' in data:
                card_member.emergency_contact_2 = data['emergency_contact_2']
            if 'emergency_contact_3' in data:
                card_member.emergency_contact_3 = data['emergency_contact_3']
            if 'status' in data:
                card_member.status = data['status']
            
            db.session.commit()
            
            branch = Branch.query.get(card_member.branch_id)
            country = Country.query.get(card_member.country_id)
            state = State.query.get(card_member.state_id)
            city = City.query.get(card_member.city_id) if card_member.city_id else None
            
            return {
                'status': 'success',
                'message': 'Card member updated successfully',
                'data': serialize_card_member(
                    card_member,
                    branch_name=branch.name if branch else None,
                    country_name=country.name if country else None,
                    state_name=state.name if state else None,
                    city_name=city.name if city else None
                )
            }, 200
            
        except Exception as e:
            db.session.rollback()
            print(f"Error updating card member: {traceback.format_exc()}")
            return {
                'status': 'fail',
                'message': f'Error updating card member: {str(e)}'
            }, 500

    @CardMembers_ns.response(200, 'Card member deleted successfully')
    @CardMembers_ns.response(404, 'Card member not found')
    @authorize('card_members.delete')  # Example permission key, adjust as needed
    def delete(self, member_id):
        """Delete a card member"""
        try:
            card_member = CardMember.query.get(member_id)
            
            if not card_member:
                return {
                    'status': 'fail',
                    'message': f'Card member with ID {member_id} not found'
                }, 404
            
            db.session.delete(card_member)
            db.session.commit()
            
            return {
                'status': 'success',
                'message': 'Card member deleted successfully',
                'data': {
                    'id': member_id
                }
            }, 200
            
        except Exception as e:
            db.session.rollback()
            print(f"Error deleting card member: {traceback.format_exc()}")
            return {
                'status': 'fail',
                'message': f'Error deleting card member: {str(e)}'
            }, 500
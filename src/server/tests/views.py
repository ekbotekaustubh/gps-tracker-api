from flask import request, abort
from flask_restx import Resource, fields, reqparse

from src.server import test_ns, db
from src.server.models import Test, Profile

# Define parser for request validation
parser = reqparse.RequestParser()
parser.add_argument('name', type=str, required=True, help='Test name is required')
parser.add_argument('analyser', type=str, help='Analyzer (pull-down from analyser)')
parser.add_argument('worklist', type=str, help='Worklist (pull-down or search from test)')
parser.add_argument('company_name', type=str, help='Company name')
parser.add_argument('price', type=float, help='Price')
parser.add_argument('range_adult_low', type=float, help='Adult low range (required if type is adult)')
parser.add_argument('range_adult_high', type=float, help='Adult high range (required if type is adult)')
parser.add_argument('type', type=str, help='Age type (infant, 7y, 12y, adult)')
parser.add_argument('gender', type=str, help='Gender (male, female, child)')
parser.add_argument('cntrl_range_selection', type=bool, help='Control range selection (y/n)')
parser.add_argument('range_ctrl_low', type=float, help='Control low range')
parser.add_argument('range_ctrl_high', type=float, help='Control high range')
parser.add_argument('range_ctrl_normal_low', type=float, help='Control normal low range')
parser.add_argument('range_ctrl_normal_high', type=float, help='Control normal high range')
parser.add_argument('department', type=str, help='Department (pull-down from department)')
parser.add_argument('unit', type=str, help='Unit (pull-down from unit)')
parser.add_argument('formula', type=str, help='Formula (default: calculator + name)')
parser.add_argument('profile_id', type=int, help='Associated profile ID')

test_model = test_ns.model('TestModel', {
    'id': fields.Integer(readonly=True),
    'name': fields.String(required=True, description='Test name'),
    'analyser': fields.String(default='Analyzer1', description='Analyzer (pull-down from analyser)'),
    'worklist': fields.String(default='Worklist1', description='Worklist (pull-down or search from test)'),
    'company_name': fields.String(default='CompanyA', description='Company name'),
    'price': fields.Float(default=150.0, description='Price'),
    'range_adult_low': fields.Float(default=8.0, description='Adult low range (required if type is adult)'),
    'range_adult_high': fields.Float(default=16.0, description='Adult high range (required if type is adult)'),
    'type': fields.String(default='adult', description='Age type (infant, 7y, 12y, adult)', enum=['adult', '7y', '12y', 'infant']),
    'gender': fields.String(default='male', description='Gender (male, female, child)', enum=['male', 'female', 'child']),
    'cntrl_range_selection': fields.Boolean(default=True, description='Control range selection (y/n)'),
    'range_ctrl_low': fields.Float(default=4.0, description='Control low range'),
    'range_ctrl_high': fields.Float(default=18.0, description='Control high range'),
    'range_ctrl_normal_low': fields.Float(default=9.0, description='Control normal low range'),
    'range_ctrl_normal_high': fields.Float(default=15.0, description='Control normal high range'),
    'department': fields.String(default='Pathology', description='Department (pull-down from department)'),
    'unit': fields.String(default='mg/dL', description='Unit (pull-down from unit)'),
    'formula': fields.String(default='calculator + string', description='Formula (default: calculator + name)'),
    'profile_id': fields.Integer(default=1, description='Associated profile ID')
    # Removed other range fields (infant, 7y, 12y) from the model to minimize display
})

@test_ns.route('')
class TestListAPI(Resource):
    @test_ns.expect(test_model, validate=True)
    @test_ns.response(201, 'Test successfully created')
    @test_ns.response(400, 'Invalid input')
    def post(self):
        """Create a new test"""
        data = request.get_json()
        if not data or 'name' not in data:
            abort(400, description="Test name is required")

        test_name = data.get('name')
        existing_test = Test.query.filter_by(name=test_name).first()
        if existing_test:
            abort(400, description="Test with this name already exists. Use PUT to update.")

        # Validate type and gender
        valid_types = ['infant', '7y', '12y', 'adult']
        valid_genders = ['male', 'female', 'child']
        test_type = data.get('type', 'adult')  # Default to 'adult' if not provided
        gender = data.get('gender', 'male')    # Default to 'male' if not provided
        if test_type not in valid_types:
            abort(400, description="Invalid type. Must be one of: infant, 7y, 12y, adult")
        if gender not in valid_genders:
            abort(400, description="Invalid gender. Must be one of: male, female, child")

        # Validate relevant range fields based on type
        range_fields = {
            'infant': ['range_infant_low', 'range_infant_high'],
            '7y': ['range_7y_low', 'range_7y_high'],
            '12y': ['range_12y_low', 'range_12y_high'],
            'adult': ['range_adult_low', 'range_adult_high']
        }
        required_ranges = range_fields.get(test_type, [])
        for field in required_ranges:
            if field not in data or data[field] is None:
                abort(400, description=f"{field} is required for type {test_type}")

        # Check for irrelevant range fields (only for non-default types to allow flexibility)
        all_range_fields = ['range_infant_low', 'range_infant_high', 'range_7y_low', 'range_7y_high',
                           'range_12y_low', 'range_12y_high', 'range_adult_low', 'range_adult_high']
        if test_type != 'adult':  # Only check if type is changed from default
            for field in all_range_fields:
                if field not in required_ranges and field in data and data[field] is not None:
                    abort(400, description=f"{field} is not applicable for type {test_type}")

        # Validate profile_id if provided
        profile_id = data.get('profile_id')
        if profile_id is not None and not Profile.query.get(profile_id):
            abort(400, description="Profile ID does not exist")

        new_test = Test(
            name=test_name,
            analyser=data.get('analyser'),
            worklist=data.get('worklist'),
            company_name=data.get('company_name'),
            price=data.get('price'),
            range_infant_low=data.get('range_infant_low'),
            range_infant_high=data.get('range_infant_high'),
            range_7y_low=data.get('range_7y_low'),
            range_7y_high=data.get('range_7y_high'),
            range_12y_low=data.get('range_12y_low'),
            range_12y_high=data.get('range_12y_high'),
            range_adult_low=data.get('range_adult_low'),
            range_adult_high=data.get('range_adult_high'),
            type=test_type,
            gender=gender,
            cntrl_range_selection=data.get('cntrl_range_selection'),
            range_ctrl_low=data.get('range_ctrl_low'),
            range_ctrl_high=data.get('range_ctrl_high'),
            range_ctrl_normal_low=data.get('range_ctrl_normal_low'),
            range_ctrl_normal_high=data.get('range_ctrl_normal_high'),
            department=data.get('department'),
            unit=data.get('unit'),
            formula=data.get('formula', f'calculator + {test_name}'),
            profile_id=profile_id
        )
        db.session.add(new_test)

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            abort(500, description=str(e))

        return {'message': 'Test created successfully', 'id': new_test.id}, 201

    @test_ns.response(200, 'Success')
    def get(self):
        """Get all tests"""
        tests = Test.query.all()
        return [{
            'id': t.id,
            'name': t.name,
            'analyser': t.analyser,
            'worklist': t.worklist,
            'company_name': t.company_name,
            'price': t.price,
            'range_infant_low': t.range_infant_low,
            'range_infant_high': t.range_infant_high,
            'range_7y_low': t.range_7y_low,
            'range_7y_high': t.range_7y_high,
            'range_12y_low': t.range_12y_low,
            'range_12y_high': t.range_12y_high,
            'range_adult_low': t.range_adult_low,
            'range_adult_high': t.range_adult_high,
            'type': t.type,
            'gender': t.gender,
            'cntrl_range_selection': t.cntrl_range_selection,
            'range_ctrl_low': t.range_ctrl_low,
            'range_ctrl_high': t.range_ctrl_high,
            'range_ctrl_normal_low': t.range_ctrl_normal_low,
            'range_ctrl_normal_high': t.range_ctrl_normal_high,
            'department': t.department,
            'unit': t.unit,
            'formula': t.formula,
            'profile_id': t.profile_id
        } for t in tests], 200

@test_ns.route('/<int:id>')
class TestAPI(Resource):
    @test_ns.response(200, 'Success')
    @test_ns.response(404, 'Test not found')
    def get(self, id):
        """Get test details by ID"""
        test = Test.query.get_or_404(id)
        return {
            'id': test.id,
            'name': test.name,
            'analyser': test.analyser,
            'worklist': test.worklist,
            'company_name': test.company_name,
            'price': test.price,
            'range_infant_low': test.range_infant_low,
            'range_infant_high': test.range_infant_high,
            'range_7y_low': test.range_7y_low,
            'range_7y_high': test.range_7y_high,
            'range_12y_low': test.range_12y_low,
            'range_12y_high': t.range_12y_high,
            'range_adult_low': test.range_adult_low,
            'range_adult_high': test.range_adult_high,
            'type': test.type,
            'gender': test.gender,
            'cntrl_range_selection': test.cntrl_range_selection,
            'range_ctrl_low': test.range_ctrl_low,
            'range_ctrl_high': test.range_ctrl_high,
            'range_ctrl_normal_low': test.range_ctrl_normal_low,
            'range_ctrl_normal_high': test.range_ctrl_normal_high,
            'department': test.department,
            'unit': test.unit,
            'formula': test.formula,
            'profile_id': test.profile_id
        }, 200

    @test_ns.expect(test_model)
    @test_ns.response(200, 'Test updated successfully')
    @test_ns.response(404, 'Test not found')
    def put(self, id):
        """Update test information"""
        test = Test.query.get_or_404(id)
        data = request.get_json()
        try:
            for key, value in data.items():
                setattr(test, key, value)
            db.session.commit()
            return {'message': 'Test updated successfully'}, 200
        except Exception as e:
            db.session.rollback()
            abort(500, description=str(e))

    @test_ns.response(200, 'Test deleted successfully')
    @test_ns.response(404, 'Test not found')
    def delete(self, id):
        """Delete a test"""
        test = Test.query.get_or_404(id)
        try:
            db.session.delete(test)
            db.session.commit()
            return {'message': 'Test deleted successfully'}, 200
        except Exception as e:
            db.session.rollback()
            abort(500, description=str(e))
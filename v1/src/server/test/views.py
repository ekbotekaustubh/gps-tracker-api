from flask import request, abort
from flask_restx import Resource, fields

from src.server import test_ns  # Import test_ns from __init__.py
from src.server import db
from src.server.models import Test

# Define a model for the Test structure
test_model = test_ns.model('TestModel', {
    'id': fields.Integer(readonly=True),
    'name': fields.String(required=True, description='Test name'),
    'analyser': fields.String(description='Analyzer'),
    'worklist': fields.String(description='Worklist'),
    'company_name': fields.String(description='Company name'),
    'price': fields.Float(description='Price'),
    'type': fields.String(description='Age type (infant, 7y, 12y, adult)'),
    'range_infant_low': fields.Float(description='Infant low range'),
    'range_infant_high': fields.Float(description='Infant high range'),
    'range_7y_low': fields.Float(description='7 years low range'),
    'range_7y_high': fields.Float(description='7 years high range'),
    'range_12y_low': fields.Float(description='12 years low range'),
    'range_12y_high': fields.Float(description='12 years high range'),
    'range_adult_low': fields.Float(description='Adult low range'),
    'range_adult_high': fields.Float(description='Adult high range'),
    'gender': fields.String(description='Gender (male, female, child)'),
    'cntrl_range_selection': fields.Boolean(description='Control range selection (y/n)'),
    'range_ctrl_low': fields.Float(description='Control low range'),
    'range_ctrl_high': fields.Float(description='Control high range'),
    'range_ctrl_normal_low': fields.Float(description='Control normal low range'),
    'range_ctrl_normal_high': fields.Float(description='Control normal high range'),
    'department': fields.String(description='Department'),
    'unit': fields.String(description='Unit'),
    'formula': fields.String(description='Formula for calculation')
})

@test_ns.route('')
class TestListAPI(Resource):
    @test_ns.expect(test_model)
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

        new_test = Test(
            name=test_name,
            analyser=data.get('analyser'),
            worklist=data.get('worklist'),
            company_name=data.get('company_name'),
            price=data.get('price'),
            type=data.get('type'),
            range_infant_low=data.get('range_infant_low'),
            range_infant_high=data.get('range_infant_high'),
            range_7y_low=data.get('range_7y_low'),
            range_7y_high=data.get('range_7y_high'),
            range_12y_low=data.get('range_12y_low'),
            range_12y_high=data.get('range_12y_high'),
            range_adult_low=data.get('range_adult_low'),
            range_adult_high=data.get('range_adult_high'),
            gender=data.get('gender'),
            cntrl_range_selection=data.get('cntrl_range_selection'),
            range_ctrl_low=data.get('range_ctrl_low'),
            range_ctrl_high=data.get('range_ctrl_high'),
            range_ctrl_normal_low=data.get('range_ctrl_normal_low'),
            range_ctrl_normal_high=data.get('range_ctrl_normal_high'),
            department=data.get('department'),
            unit=data.get('unit'),
            formula=data.get('formula', f'calculator + {test_name}')  # Default formula
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
            'type': t.type,
            'range_infant_low': t.range_infant_low,
            'range_infant_high': t.range_infant_high,
            'range_7y_low': t.range_7y_low,
            'range_7y_high': t.range_7y_high,
            'range_12y_low': t.range_12y_low,
            'range_12y_high': t.range_12y_high,
            'range_adult_low': t.range_adult_low,
            'range_adult_high': t.range_adult_high,
            'gender': t.gender,
            'cntrl_range_selection': t.cntrl_range_selection,
            'range_ctrl_low': t.range_ctrl_low,
            'range_ctrl_high': t.range_ctrl_high,
            'range_ctrl_normal_low': t.range_ctrl_normal_low,
            'range_ctrl_normal_high': t.range_ctrl_normal_high,
            'department': t.department,
            'unit': t.unit,
            'formula': t.formula
        } for t in tests], 200

    @test_ns.expect(test_model)
    @test_ns.response(200, 'Test successfully updated')
    @test_ns.response(400, 'Invalid input or test not found')
    @test_ns.response(404, 'Test not found')
    def put(self):
        """Update an existing test"""
        data = request.get_json()
        if not data or 'id' not in data or 'name' not in data:
            abort(400, description="Test ID and name are required")

        test_id = data.get('id')
        test = Test.query.get(test_id)
        if not test:
            abort(404, description="Test not found")

        test.name = data.get('name')
        test.analyser = data.get('analyser')
        test.worklist = data.get('worklist')
        test.company_name = data.get('company_name')
        test.price = data.get('price')
        test.type = data.get('type')
        test.range_infant_low = data.get('range_infant_low')
        test.range_infant_high = data.get('range_infant_high')
        test.range_7y_low = data.get('range_7y_low')
        test.range_7y_high = data.get('range_7y_high')
        test.range_12y_low = data.get('range_12y_low')
        test.range_12y_high = data.get('range_12y_high')
        test.range_adult_low = data.get('range_adult_low')
        test.range_adult_high = data.get('range_adult_high')
        test.gender = data.get('gender')
        test.cntrl_range_selection = data.get('cntrl_range_selection')
        test.range_ctrl_low = data.get('range_ctrl_low')
        test.range_ctrl_high = data.get('range_ctrl_high')
        test.range_ctrl_normal_low = data.get('range_ctrl_normal_low')
        test.range_ctrl_normal_high = data.get('range_ctrl_normal_high')
        test.department = data.get('department')
        test.unit = data.get('unit')
        test.formula = data.get('formula', f'calculator + {data.get("name")}')

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            abort(500, description=str(e))

        return {'message': 'Test updated successfully', 'id': test.id}, 200

    @test_ns.response(200, 'Test successfully deleted')
    @test_ns.response(404, 'Test not found')
    def delete(self):
        """Delete a test by ID"""
        data = request.get_json()
        if not data or 'id' not in data:
            abort(400, description="Test ID is required")

        test_id = data.get('id')
        test = Test.query.get(test_id)
        if not test:
            abort(404, description="Test not found")

        try:
            db.session.delete(test)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            abort(500, description=str(e))

        return {'message': 'Test deleted successfully', 'id': test_id}, 200
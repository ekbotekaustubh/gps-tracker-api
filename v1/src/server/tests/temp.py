
class Test(db.Model):
    __tablename__ = "tests"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    group_name = db.Column(db.String(255), nullable=True)
    profile_na = db.Column(db.String(255), nullable=True)
    analyser_mobile = db.Column(db.String(50), nullable=True)
    range_m_h = db.Column(db.Float, nullable=True)
    range_f_h = db.Column(db.Float, nullable=True)
    range_f_l = db.Column(db.Float, nullable=True)
    range_c_h = db.Column(db.Float, nullable=True)
    range_c_l = db.Column(db.Float, nullable=True)
    units = db.Column(db.String(50), nullable=True)
    price = db.Column(db.Float, nullable=True)
    range_ctr_1 = db.Column(db.Float, nullable=True)
    range_ctr_2 = db.Column(db.Float, nullable=True)
    range_ctr_3 = db.Column(db.Float, nullable=True)
    volume = db.Column(db.Float, nullable=True)

    def __init__(self, name, abbr_1st_unique_te_company_na=None, profile_na=None, 
                 analyser_mobile=None, range_m_h=None, range_f_h=None, range_f_l=None, 
                 range_c_h=None, range_c_l=None, units=None, price=None, 
                 range_ctr_1=None, range_ctr_2=None, range_ctr_3=None, volume=None):
        self.name = name
        self.abbr_1st_unique_te_company_na = abbr_1st_unique_te_company_na
        self.profile_na = profile_na
        self.analyser_mobile = analyser_mobile
        self.range_m_h = range_m_h
        self.range_f_h = range_f_h
        self.range_f_l = range_f_l
        self.range_c_h = range_c_h
        self.range_c_l = range_c_l
        self.units = units
        self.price = price
        self.range_ctr_1 = range_ctr_1
        self.range_ctr_2 = range_ctr_2
        self.range_ctr_3 = range_ctr_3
        self.volume = volume

        # project/server/test/views.py

import traceback
import inspect

from flask import Blueprint, request, make_response, jsonify, g
from flask.views import MethodView
from flask_restx import Resource, fields

from src.server import bcrypt, db
from src.server.models import Profile, Test, BlacklistToken
from src.server import test_ns

test_blueprint = Blueprint('test', __name__)

# Define Swagger models
test_model = test_ns.model('Test', {
    'name': fields.String(required=True, description='Test name'),
    'abbr_1st_unique_te_company_na': fields.String(description='Abbreviation'),
    'profile_na': fields.String(description='Profile name'),
    'analyser_mobile': fields.String(description='Analyser mobile'),
    'range_m_h': fields.Float(description='Male higher range'),
    'range_f_h': fields.Float(description='Female higher range'),
    'range_f_l': fields.Float(description='Female lower range'),
    'range_c_h': fields.Float(description='Child higher range'),
    'range_c_l': fields.Float(description='Child lower range'),
    'units': fields.String(description='Units'),
    'price': fields.Float(description='Price'),
    'extra': fields.String(description='Extra information')
})

@test_ns.route('')
class TestListAPI(Resource):
    @test_ns.expect(test_model)
    @test_ns.response(201, 'Test successfully created')
    @test_ns.response(400, 'Invalid input')
    def post(self):
        """Create a new test"""
        data = request.get_json()
        try:
            test = Test(**data)
            db.session.add(test)
            db.session.commit()
            return {'message': 'Test created successfully', 'id': test.id}, 201
        except Exception as e:
            db.session.rollback()
            return {'message': str(e)}, 400

    @test_ns.response(200, 'Success')
    def get(self):
        """Get all tests"""
        tests = Test.query.all()
        return [{
            'id': t.id,
            'name': t.name,
            'abbr_1st_unique_te_company_na': t.abbr_1st_unique_te_company_na,
            'price': t.price
        } for t in tests], 200

@test_ns.route('/<int:id>')
class TestAPI(Resource):
    @test_ns.response(200, 'Success')
    @test_ns.response(404, 'Test not found')
    def get(self, id):
        """Get test details"""
        test = Test.query.get_or_404(id)
        return {
            'id': test.id,
            'name': test.name,
            'abbr_1st_unique_te_company_na': test.abbr_1st_unique_te_company_na,
            'profile_na': test.profile_na,
            'analyser_mobile': test.analyser_mobile,
            'range_m_h': test.range_m_h,
            'range_f_h': test.range_f_h,
            'range_f_l': test.range_f_l,
            'range_c_h': test.range_c_h,
            'range_c_l': test.range_c_l,
            'units': test.units,
            'price': test.price,
            'extra': test.extr
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
            return {'message': str(e)}, 400

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
            return {'message': str(e)}, 400

# Register the API endpoints
test_view = TestAPI.as_view('test_api')

# Define the API resources
test_blueprint.add_url_rule(
    '/test',
    view_func=test_view,
    methods=['GET', 'POST']  # GET (all tests), POST (create)
)

test_blueprint.add_url_rule(
    '/test/<int:test_id>',
    view_func=test_view,
    methods=['GET', 'PUT', 'DELETE']  # GET (single test), PUT (update), DELETE (delete)
)

# project/server/patient/views.py

import traceback
import inspect

from flask import Blueprint, request, make_response, jsonify, g
from flask.views import MethodView
from flask_restx import Resource, fields

from src.server import bcrypt, db
from src.server.models import Patient, BlacklistToken
from src.server import patient_ns

patient_blueprint = Blueprint('patient', __name__)

# Define Swagger models
patient_model = patient_ns.model('Patient', {
    'name': fields.String(required=True, description='Patient name'),
    'sname': fields.String(required=True, description='Patient surname'),
    'aadhar': fields.String(description='Aadhar number'),
    'email': fields.String(description='Email address'),
    'mobile': fields.String(description='Mobile number'),
    'nation_id': fields.String(description='National ID'),
    'date': fields.String(required=True, description='Registration date'),
    'patient_type': fields.String(required=True, description='Type of patient'),
    'age_group': fields.String(description='Age group'),
    'date_of_birth': fields.String(description='Date of birth'),
    'age': fields.Integer(description='Age'),
    'gender': fields.String(description='Gender'),
    'reference': fields.String(description='Reference'),
    'id_address': fields.String(description='ID address')
})

@patient_ns.route('')
class PatientListAPI(Resource):
    @patient_ns.expect(patient_model)
    @patient_ns.response(201, 'Patient successfully created')
    @patient_ns.response(400, 'Invalid input')
    def post(self):
        """Create a new patient"""
        data = request.get_json()
        try:
            # Validate required fields
            required_fields = ['name', 'sname', 'date', 'patient_type']
            for field in required_fields:
                if field not in data:
                    return {'message': f'Missing required field: {field}'}, 400

            # Convert date string to datetime object
            try:
                from datetime import datetime
                date = datetime.strptime(data['date'], '%Y-%m-%d')
            except ValueError:
                return {'message': 'Invalid date format. Use YYYY-MM-DD'}, 400

            # Create patient with required fields
            patient = Patient(
                name=data['name'],
                sname=data['sname'],
                date=date,
                patient_type=data['patient_type']
            )

            # Add optional fields if provided
            optional_fields = ['aadhar', 'email', 'mobile', 'nation_id', 'age_group', 
                             'date_of_birth', 'age', 'gender', 'reference', 'id_address']
            for field in optional_fields:
                if field in data:
                    if field == 'date_of_birth' and data[field]:
                        try:
                            data[field] = datetime.strptime(data[field], '%Y-%m-%d')
                        except ValueError:
                            return {'message': 'Invalid date_of_birth format. Use YYYY-MM-DD'}, 400
                    setattr(patient, field, data[field])

            db.session.add(patient)
            db.session.commit()
            return {'message': 'Patient created successfully', 'id': patient.id}, 201
        except Exception as e:
            db.session.rollback()
            return {'message': str(e)}, 400

    @patient_ns.response(200, 'Success')
    def get(self):
        """Get all patients"""
        patients = Patient.query.all()
        return [{
            'id': p.id,
            'name': p.name,
            'sname': p.sname,
            'email': p.email,
            'mobile': p.mobile,
            'patient_type': p.patient_type
        } for p in patients], 200

@patient_ns.route('/<int:id>')
class PatientAPI(Resource):
    @patient_ns.response(200, 'Success')
    @patient_ns.response(404, 'Patient not found')
    def get(self, id):
        """Get patient details"""
        patient = Patient.query.get_or_404(id)
        return {
            'id': patient.id,
            'name': patient.name,
            'sname': patient.sname,
            'aadhar': patient.aadhar,
            'email': patient.email,
            'mobile': patient.mobile,
            'nation_id': patient.nation_id,
            'date': patient.date,
            'patient_type': patient.patient_type,
            'age_group': patient.age_group,
            'date_of_birth': patient.date_of_birth,
            'age': patient.age,
            'gender': patient.gender,
            'reference': patient.reference,
            'id_address': patient.id_address
        }, 200

    @patient_ns.expect(patient_model)
    @patient_ns.response(200, 'Patient updated successfully')
    @patient_ns.response(404, 'Patient not found')
    def put(self, id):
        """Update patient information"""
        patient = Patient.query.get_or_404(id)
        data = request.get_json()
        try:
            for key, value in data.items():
                setattr(patient, key, value)
            db.session.commit()
            return {'message': 'Patient updated successfully'}, 200
        except Exception as e:
            db.session.rollback()
            return {'message': str(e)}, 400

    @patient_ns.response(200, 'Patient deleted successfully')
    @patient_ns.response(404, 'Patient not found')
    def delete(self, id):
        """Delete a patient"""
        patient = Patient.query.get_or_404(id)
        try:
            db.session.delete(patient)
            db.session.commit()
            return {'message': 'Patient deleted successfully'}, 200
        except Exception as e:
            db.session.rollback()
            return {'message': str(e)}, 400

# Register the API endpoint
patient_view = PatientAPI.as_view('patient_api')

# define the API resources
patient_blueprint.add_url_rule('/patient/add', 
                 view_func=patient_view, 
                 methods=['POST']
                 )
    

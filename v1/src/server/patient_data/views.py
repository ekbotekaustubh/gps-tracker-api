from flask import request, abort
from flask_restx import Resource, Namespace, fields, reqparse
from sqlalchemy import and_
from datetime import datetime

from src.server import db
from src.server.models import PatientDataEntry, Profile, Test, Package

patient_data_ns = Namespace('patient_data', description='Patient data entry operations')

# Define the model for the API
patient_model = patient_data_ns.model('PatientDataEntryModel', {
    'id': fields.Integer(readonly=True),
    'ref': fields.String(description='Reference'),
    'today_date': fields.DateTime(description='Today\'s date'),
    'id_name': fields.String(description='ID name'),
    'id_value': fields.String(description='ID value'),
    'gender': fields.String(description='Gender', enum=['male', 'female', 'child']),
    'dob': fields.DateTime(description='Date of birth'),
    'age': fields.String(description='Age'),
    'mobile': fields.String(description='Mobile number'),
    'address': fields.String(description='Address'),
    'aadhar': fields.String(description='Aadhar number'),
    'national_id': fields.String(description='National ID'),
    'work_profs': fields.List(fields.String, description='Selected work profiles (multiple, optional)'),
    'work_lists': fields.List(fields.String, description='Selected work lists (multiple, optional)'),
    'task_lists': fields.List(fields.String, description='Selected tasks (multiple, required)')
})

# Parser for request validation
parser = reqparse.RequestParser()
parser.add_argument('ref', type=str, help='Reference')
parser.add_argument('today_date', type=str, help='Today\'s date (ISO format)')
parser.add_argument('id_name', type=str, help='ID name')
parser.add_argument('id_value', type=str, help='ID value')
parser.add_argument('gender', type=str, help='Gender (male, female, child)')
parser.add_argument('dob', type=str, help='Date of birth (ISO format)')
parser.add_argument('age', type=str, help='Age')
parser.add_argument('mobile', type=str, help='Mobile number')
parser.add_argument('address', type=str, help='Address')
parser.add_argument('aadhar', type=str, help='Aadhar number')
parser.add_argument('national_id', type=str, help='National ID')
parser.add_argument('work_profs', type=list, location='json', help='Selected work profiles (multiple, optional)')
parser.add_argument('work_lists', type=list, location='json', help='Selected work lists (multiple, optional)')
parser.add_argument('task_lists', type=list, location='json', required=True, help='Selected tasks (multiple, required)')

# Custom error response function to avoid verbose messages
def custom_abort(status, description):
    abort(status, description=description)

# Resource for collection-level operations (GET all, POST)
@patient_data_ns.route('/patient_data_entry')
class PatientDataEntryCollectionAPI(Resource):
    @patient_data_ns.response(200, 'Patient data entries retrieved successfully')
    def get(self):
        """Retrieve all patient data entries"""
        entries = PatientDataEntry.query.all()
        return [{
            'id': entry.id,
            'ref': entry.ref,
            'today_date': entry.today_date.isoformat() if entry.today_date else None,
            'id_name': entry.id_name,
            'id_value': entry.id_value,
            'gender': entry.gender,
            'dob': entry.dob.isoformat() if entry.dob else None,
            'age': entry.age,
            'mobile': entry.mobile,
            'address': entry.address,
            'aadhar': entry.aadhar,
            'national_id': entry.national_id,
            'work_profs': [p.work_prof for p in entry.work_profs],
            'work_lists': [p.worklist for p in entry.work_lists],
            'task_lists': [t.name for t in entry.task_lists]
        } for entry in entries], 200

    @patient_data_ns.expect(patient_model, validate=True)
    @patient_data_ns.response(201, 'Patient data entry successfully created')
    @patient_data_ns.response(400, 'Invalid input')
    def post(self):
        """Create a new patient data entry"""
        data = request.get_json()
        if not data or 'task_lists' not in data or not data['task_lists']:
            custom_abort(400, "Task lists are required")

        # Parse date strings to datetime objects
        today_date = datetime.fromisoformat(data.get('today_date').replace('Z', '+00:00')) if data.get('today_date') else None
        dob = datetime.fromisoformat(data.get('dob').replace('Z', '+00:00')) if data.get('dob') else None

        work_prof_objects = []
        if data.get('work_profs'):
            work_prof_objects = Profile.query.filter(Profile.work_prof.in_(data['work_profs'])).all()
            if len(work_prof_objects) != len(data['work_profs']):
                custom_abort(400, "One or more work profiles not found")

        work_list_objects = []
        if data.get('work_lists'):
            work_list_objects = Package.query.filter(Package.worklist.in_(data['work_lists'])).all()
            if len(work_list_objects) != len(data['work_lists']):
                custom_abort(400, "One or more work lists not found")

        task_objects = Test.query.filter(Test.name.in_(data['task_lists'])).all()
        if len(task_objects) != len(data['task_lists']):
            custom_abort(400, "One or more tasks not found")

        new_entry = PatientDataEntry(
            ref=data.get('ref'),
            today_date=today_date,
            id_name=data.get('id_name'),
            id_value=data.get('id_value'),
            gender=data.get('gender'),
            dob=dob,
            age=data.get('age'),
            mobile=data.get('mobile'),
            address=data.get('address'),
            aadhar=data.get('aadhar'),
            national_id=data.get('national_id')
        )
        new_entry.work_profs = work_prof_objects
        new_entry.work_lists = work_list_objects
        new_entry.task_lists = task_objects

        db.session.add(new_entry)
        try:
            db.session.commit()
            return {'message': 'Patient data entry created successfully', 'id': new_entry.id}, 201
        except Exception as e:
            db.session.rollback()
            custom_abort(500, str(e))

# Resource for item-level operations (GET by ID, PUT, DELETE)
@patient_data_ns.route('/patient_data_entry/<int:id>')
class PatientDataEntryItemAPI(Resource):
    @patient_data_ns.response(200, 'Patient data entry retrieved successfully')
    @patient_data_ns.response(404, 'Patient data entry not found')
    def get(self, id):
        """Retrieve a specific patient data entry by ID"""
        entry = PatientDataEntry.query.get_or_404(id)
        return {
            'id': entry.id,
            'ref': entry.ref,
            'today_date': entry.today_date.isoformat() if entry.today_date else None,
            'id_name': entry.id_name,
            'id_value': entry.id_value,
            'gender': entry.gender,
            'dob': entry.dob.isoformat() if entry.dob else None,
            'age': entry.age,
            'mobile': entry.mobile,
            'address': entry.address,
            'aadhar': entry.aadhar,
            'national_id': entry.national_id,
            'work_profs': [p.work_prof for p in entry.work_profs],
            'work_lists': [p.worklist for p in entry.work_lists],
            'task_lists': [t.name for t in entry.task_lists]
        }, 200

    @patient_data_ns.expect(patient_model, validate=True)
    @patient_data_ns.response(200, 'Patient data entry updated successfully')
    @patient_data_ns.response(404, 'Patient data entry not found')
    @patient_data_ns.response(400, 'Invalid input')
    def put(self, id):
        """Update an existing patient data entry"""
        entry = PatientDataEntry.query.get_or_404(id)
        data = request.get_json()
        if not data or 'task_lists' not in data or not data['task_lists']:
            custom_abort(400, "Task lists are required")

        # Parse date strings to datetime objects
        today_date = datetime.fromisoformat(data.get('today_date').replace('Z', '+00:00')) if data.get('today_date') else entry.today_date
        dob = datetime.fromisoformat(data.get('dob').replace('Z', '+00:00')) if data.get('dob') else entry.dob

        work_prof_objects = []
        if data.get('work_profs'):
            work_prof_objects = Profile.query.filter(Profile.work_prof.in_(data['work_profs'])).all()
            if len(work_prof_objects) != len(data['work_profs']):
                custom_abort(400, "One or more work profiles not found")

        work_list_objects = []
        if data.get('work_lists'):
            work_list_objects = Package.query.filter(Package.worklist.in_(data['work_lists'])).all()
            if len(work_list_objects) != len(data['work_lists']):
                custom_abort(400, "One or more work lists not found")

        task_objects = Test.query.filter(Test.name.in_(data['task_lists'])).all()
        if len(task_objects) != len(data['task_lists']):
            custom_abort(400, "One or more tasks not found")

        entry.ref = data.get('ref', entry.ref)
        entry.today_date = today_date
        entry.id_name = data.get('id_name', entry.id_name)
        entry.id_value = data.get('id_value', entry.id_value)
        entry.gender = data.get('gender', entry.gender)
        entry.dob = dob
        entry.age = data.get('age', entry.age)
        entry.mobile = data.get('mobile', entry.mobile)
        entry.address = data.get('address', entry.address)
        entry.aadhar = data.get('aadhar', entry.aadhar)
        entry.national_id = data.get('national_id', entry.national_id)
        entry.work_profs = work_prof_objects
        entry.work_lists = work_list_objects
        entry.task_lists = task_objects

        try:
            db.session.commit()
            return {'message': 'Patient data entry updated successfully'}, 200
        except Exception as e:
            db.session.rollback()
            custom_abort(500, str(e))

    @patient_data_ns.response(200, 'Patient data entry deleted successfully')
    @patient_data_ns.response(404, 'Patient data entry not found')
    def delete(self, id):
        """Delete an existing patient data entry"""
        entry = PatientDataEntry.query.get_or_404(id)
        db.session.delete(entry)
        try:
            db.session.commit()
            return {'message': 'Patient data entry deleted successfully'}, 200
        except Exception as e:
            db.session.rollback()
            custom_abort(500, str(e))

# Resource for filtered options
@patient_data_ns.route('/patient_data_entry/filtered_options')
class PatientDataEntryFilteredOptionsAPI(Resource):
    @patient_data_ns.response(200, 'Success')
    def get(self):
        """Get filtered options based on selected work_profs and work_lists"""
        args = parser.parse_args()
        work_profs = args.get('work_profs', [])
        work_lists = args.get('work_lists', [])

        profiles = Profile.query.filter(Profile.work_prof.in_(work_profs)).all() if work_profs else []
        profile_ids = [p.id for p in profiles]

        tests = Test.query.filter(Test.profile_id.in_(profile_ids)).all() if profile_ids else Test.query.all()

        if work_lists:
            packages = Package.query.filter(Package.worklist.in_(work_lists)).all()
            package_ids = [p.id for p in packages]
            tests = [t for t in tests if t.profile_id in package_ids]

        task_lists = [t.name for t in tests]
        return {'task_lists': task_lists}, 200
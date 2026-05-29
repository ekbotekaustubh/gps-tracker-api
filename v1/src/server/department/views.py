from flask import request, abort
from flask_restx import Resource, fields

from src.server import department_ns, db
from src.server.models import Department, Analyser

department_model = department_ns.model('DepartmentModel', {
    'id': fields.Integer(readonly=True),
    'name': fields.String(description='Department name (enter/search stru-depart)'),
    'hod_name': fields.String(description='Head of Department name'),
    'mobile': fields.String(description='Mobile number'),
    'no_of_analyser': fields.Integer(description='Number of analysers')
})

analyser_model = department_ns.model('AnalyserModel', {
    'id': fields.Integer(readonly=True),
    'name': fields.String(description='Analyser name'),
    'department_id': fields.Integer(default=1, description='Associated department ID')  # Changed default from 0 to 1
})

@department_ns.route('/departments')
class DepartmentListAPI(Resource):
    @department_ns.expect(department_model)
    @department_ns.response(201, 'Department successfully created')
    @department_ns.response(400, 'Invalid input')
    def post(self):
        """Create a new department"""
        data = request.get_json()
        if not data or 'name' not in data:
            abort(400, description="Department name is required")

        name = data.get('name')
        existing_department = Department.query.filter_by(name=name).first()
        if existing_department:
            abort(400, description="Department with this name already exists. Use PUT to update.")

        new_department = Department(
            name=name,
            hod_name=data.get('hod_name'),
            mobile=data.get('mobile'),
            no_of_analyser=data.get('no_of_analyser')
        )
        db.session.add(new_department)

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            abort(500, description=str(e))

        return {'message': 'Department created successfully', 'id': new_department.id}, 201

    @department_ns.response(200, 'Success')
    def get(self):
        """Get all departments"""
        departments = Department.query.all()
        return [{
            'id': d.id,
            'name': d.name,
            'hod_name': d.hod_name,
            'mobile': d.mobile,
            'no_of_analyser': d.no_of_analyser
        } for d in departments], 200

@department_ns.route('/departments/<int:id>')
class DepartmentAPI(Resource):
    @department_ns.response(200, 'Success')
    @department_ns.response(404, 'Department not found')
    def get(self, id):
        """Get department details by ID"""
        department = Department.query.get_or_404(id)
        return {
            'id': department.id,
            'name': department.name,
            'hod_name': department.hod_name,
            'mobile': department.mobile,
            'no_of_analyser': department.no_of_analyser
        }, 200

    @department_ns.expect(department_model)
    @department_ns.response(200, 'Department updated successfully')
    @department_ns.response(404, 'Department not found')
    def put(self, id):
        """Update department information"""
        department = Department.query.get_or_404(id)
        data = request.get_json()
        try:
            for key, value in data.items():
                setattr(department, key, value)
            db.session.commit()
            return {'message': 'Department updated successfully'}, 200
        except Exception as e:
            db.session.rollback()
            abort(500, description=str(e))

    @department_ns.response(200, 'Department deleted successfully')
    @department_ns.response(404, 'Department not found')
    def delete(self, id):
        """Delete a department"""
        department = Department.query.get_or_404(id)
        try:
            db.session.delete(department)
            db.session.commit()
            return {'message': 'Department deleted successfully'}, 200
        except Exception as e:
            db.session.rollback()
            abort(500, description=str(e))

@department_ns.route('/analysers')
class AnalyserListAPI(Resource):
    @department_ns.expect(analyser_model)
    @department_ns.response(201, 'Analyser successfully created')
    @department_ns.response(400, 'Invalid input')
    def post(self):
        """Create a new analyser"""
        data = request.get_json()
        if not data or 'name' not in data:
            abort(400, description="Analyser name is required")

        name = data.get('name')
        department_id = data.get('department_id')
        if department_id is not None and not Department.query.get(department_id):
            abort(400, description="Department ID does not exist")

        new_analyser = Analyser(
            name=name,
            department_id=department_id  # Use provided value or None
        )
        db.session.add(new_analyser)

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            abort(500, description=str(e))

        return {'message': 'Analyser created successfully', 'id': new_analyser.id}, 201

    @department_ns.response(200, 'Success')
    def get(self):
        """Get all analysers"""
        analysers = Analyser.query.all()
        return [{
            'id': a.id,
            'name': a.name,
            'department_id': a.department_id
        } for a in analysers], 200
from flask import request, abort
from flask_restx import Resource, fields

from src.server import package_ns, db
from src.server.models import Package

package_model = package_ns.model('PackageModel', {
    'id': fields.Integer(readonly=True),
    'workprof': fields.String(description='Work profile (enter/search)'),
    'no_of_wklist': fields.Integer(description='Number of worklists'),
    'worklist': fields.String(description='Worklist (list of tests stru-test)'),
    'price': fields.Float(description='Price'),
    'formula': fields.String(description='Formula (default: calculator + workprof)')
})

@package_ns.route('')
class PackageListAPI(Resource):
    @package_ns.expect(package_model)
    @package_ns.response(201, 'Package successfully created')
    @package_ns.response(400, 'Invalid input')
    def post(self):
        """Create a new package"""
        data = request.get_json()
        if not data or 'workprof' not in data:
            abort(400, description="Work profile is required")

        workprof = data.get('workprof')
        existing_package = Package.query.filter_by(workprof=workprof).first()
        if existing_package:
            abort(400, description="Package with this workprof already exists. Use PUT to update.")

        new_package = Package(
            workprof=workprof,
            no_of_wklist=data.get('no_of_wklist'),
            worklist=data.get('worklist'),
            price=data.get('price'),
            formula=data.get('formula', f'calculator + {workprof}')
        )
        db.session.add(new_package)

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            abort(500, description=str(e))

        return {'message': 'Package created successfully', 'id': new_package.id}, 201

    @package_ns.response(200, 'Success')
    def get(self):
        """Get all packages"""
        packages = Package.query.all()
        return [{
            'id': p.id,
            'workprof': p.workprof,
            'no_of_wklist': p.no_of_wklist,
            'worklist': p.worklist,
            'price': p.price,
            'formula': p.formula
        } for p in packages], 200

@package_ns.route('/<int:id>')
class PackageAPI(Resource):
    @package_ns.response(200, 'Success')
    @package_ns.response(404, 'Package not found')
    def get(self, id):
        """Get package details by ID"""
        package = Package.query.get_or_404(id)
        return {
            'id': package.id,
            'workprof': package.workprof,
            'no_of_wklist': package.no_of_wklist,
            'worklist': package.worklist,
            'price': package.price,
            'formula': package.formula
        }, 200

    @package_ns.expect(package_model)
    @package_ns.response(200, 'Package updated successfully')
    @package_ns.response(404, 'Package not found')
    def put(self, id):
        """Update package information"""
        package = Package.query.get_or_404(id)
        data = request.get_json()
        try:
            for key, value in data.items():
                setattr(package, key, value)
            db.session.commit()
            return {'message': 'Package updated successfully'}, 200
        except Exception as e:
            db.session.rollback()
            abort(500, description=str(e))

    @package_ns.response(200, 'Package deleted successfully')
    @package_ns.response(404, 'Package not found')
    def delete(self, id):
        """Delete a package"""
        package = Package.query.get_or_404(id)
        try:
            db.session.delete(package)
            db.session.commit()
            return {'message': 'Package deleted successfully'}, 200
        except Exception as e:
            db.session.rollback()
            abort(500, description=str(e))
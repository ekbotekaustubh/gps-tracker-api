from flask import request, abort
from flask_restx import Resource, fields, reqparse

from src.server import profile_ns, db
from src.server.models import Profile

# Define parser for request validation
parser = reqparse.RequestParser()
parser.add_argument('work_prof', type=str, required=True, help='Work profile is required')
parser.add_argument('no_of_wklist', type=int, help='Number of worklists')
parser.add_argument('worklist', type=str, help='Worklist (list of tests stru-test)')
parser.add_argument('price', type=float, help='Price')
parser.add_argument('range_male_low', type=float, help='Male low range (required if gender is male)')
parser.add_argument('range_male_high', type=float, help='Male high range (required if gender is male)')
parser.add_argument('range_female_low', type=float, help='Female low range (required if gender is female)')
parser.add_argument('range_female_high', type=float, help='Female high range (required if gender is female)')
parser.add_argument('range_child_low', type=float, help='Child low range (required if gender is child)')
parser.add_argument('range_child_high', type=float, help='Child high range (required if gender is child)')
parser.add_argument('gender', type=str, help='Gender (male, female, child)')
parser.add_argument('cntrl_range_selection', type=bool, help='Control range selection (y/n)')
parser.add_argument('range_ctrl_low', type=float, help='Control low range')
parser.add_argument('range_ctrl_high', type=float, help='Control high range')
parser.add_argument('range_ctrl_normal_low', type=float, help='Control normal low range')
parser.add_argument('range_ctrl_normal_high', type=float, help='Control normal high range')
parser.add_argument('formula', type=str, help='Formula (default: calculator + work_prof)')

profile_model = profile_ns.model('ProfileModel', {
    'id': fields.Integer(readonly=True),
    'work_prof': fields.String(description='Work profile (enter/search)'),
    'no_of_wklist': fields.Integer(default=5, description='Number of worklists'),
    'worklist': fields.String(default='Worklist1', description='Worklist (list of tests stru-test)'),
    'price': fields.Float(default=200.0, description='Price'),
    'range_male_low': fields.Float(default=8.0, description='Male low range (required if gender is male)'),
    'range_male_high': fields.Float(default=16.0, description='Male high range (required if gender is male)'),
    # Removed range_female_low, range_female_high, range_child_low, range_child_high from the model
    'gender': fields.String(default='male', description='Gender (male, female, child)', enum=['male', 'female', 'child']),
    'cntrl_range_selection': fields.Boolean(default=True, description='Control range selection (y/n)'),
    'range_ctrl_low': fields.Float(default=4.0, description='Control low range'),
    'range_ctrl_high': fields.Float(default=18.0, description='Control high range'),
    'range_ctrl_normal_low': fields.Float(default=9.0, description='Control normal low range'),
    'range_ctrl_normal_high': fields.Float(default=15.0, description='Control normal high range'),
    'formula': fields.String(default='calculator + string', description='Formula (default: calculator + work_prof)')
})

@profile_ns.route('')
class ProfileListAPI(Resource):
    @profile_ns.expect(profile_model, validate=True)
    @profile_ns.response(201, 'Profile successfully created')
    @profile_ns.response(400, 'Invalid input')
    def post(self):
        """Create a new profile"""
        data = request.get_json()
        if not data or 'work_prof' not in data:
            abort(400, description="Work profile is required")

        work_prof = data.get('work_prof')
        existing_profile = Profile.query.filter_by(work_prof=work_prof).first()
        if existing_profile:
            abort(400, description="Profile with this work_prof already exists. Use PUT to update.")

        # Validate gender
        valid_genders = ['male', 'female', 'child']
        gender = data.get('gender', 'male')  # Default to 'male' if not provided
        if gender not in valid_genders:
            abort(400, description="Invalid gender. Must be one of: male, female, child")

        # Validate relevant range fields based on gender
        range_fields = {
            'male': ['range_male_low', 'range_male_high'],
            'female': ['range_female_low', 'range_female_high'],
            'child': ['range_child_low', 'range_child_high']
        }
        required_ranges = range_fields.get(gender, [])
        for field in required_ranges:
            if field not in data or data[field] is None:
                abort(400, description=f"{field} is required for gender {gender}")

        # Check for irrelevant range fields (only if gender is changed from default)
        all_range_fields = ['range_male_low', 'range_male_high', 'range_female_low', 'range_female_high',
                           'range_child_low', 'range_child_high']
        if gender != 'male':  # Only check if gender is changed from default
            for field in all_range_fields:
                if field not in required_ranges and field in data and data[field] is not None:
                    abort(400, description=f"{field} is not applicable for gender {gender}")

        new_profile = Profile(
            work_prof=work_prof,
            no_of_wklist=data.get('no_of_wklist'),
            worklist=data.get('worklist'),
            price=data.get('price'),
            range_male_low=data.get('range_male_low'),
            range_male_high=data.get('range_male_high'),
            range_female_low=data.get('range_female_low'),
            range_female_high=data.get('range_female_high'),
            range_child_low=data.get('range_child_low'),
            range_child_high=data.get('range_child_high'),
            gender=gender,
            cntrl_range_selection=data.get('cntrl_range_selection'),
            range_ctrl_low=data.get('range_ctrl_low'),
            range_ctrl_high=data.get('range_ctrl_high'),
            range_ctrl_normal_low=data.get('range_ctrl_normal_low'),
            range_ctrl_normal_high=data.get('range_ctrl_normal_high'),
            formula=data.get('formula', f'calculator + {work_prof}')
        )
        db.session.add(new_profile)

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            abort(500, description=str(e))

        return {'message': 'Profile created successfully', 'id': new_profile.id}, 201

    @profile_ns.response(200, 'Success')
    def get(self):
        """Get all profiles"""
        profiles = Profile.query.all()
        return [{
            'id': p.id,
            'work_prof': p.work_prof,
            'no_of_wklist': p.no_of_wklist,
            'worklist': p.worklist,
            'price': p.price,
            'range_male_low': p.range_male_low,
            'range_male_high': p.range_male_high,
            'range_female_low': p.range_female_low,
            'range_female_high': p.range_female_high,
            'range_child_low': p.range_child_low,
            'range_child_high': p.range_child_high,
            'gender': p.gender,
            'cntrl_range_selection': p.cntrl_range_selection,
            'range_ctrl_low': p.range_ctrl_low,
            'range_ctrl_high': p.range_ctrl_high,
            'range_ctrl_normal_low': p.range_ctrl_normal_low,
            'range_ctrl_normal_high': p.range_ctrl_normal_high,
            'formula': p.formula
        } for p in profiles], 200

@profile_ns.route('/<int:id>')
class ProfileAPI(Resource):
    @profile_ns.response(200, 'Success')
    @profile_ns.response(404, 'Profile not found')
    def get(self, id):
        """Get profile details by ID"""
        profile = Profile.query.get_or_404(id)
        return {
            'id': profile.id,
            'work_prof': profile.work_prof,
            'no_of_wklist': profile.no_of_wklist,
            'worklist': profile.worklist,
            'price': profile.price,
            'range_male_low': profile.range_male_low,
            'range_male_high': p.range_male_high,
            'range_female_low': profile.range_female_low,
            'range_female_high': profile.range_female_high,
            'range_child_low': profile.range_child_low,
            'range_child_high': profile.range_child_high,
            'gender': profile.gender,
            'cntrl_range_selection': profile.cntrl_range_selection,
            'range_ctrl_low': profile.range_ctrl_low,
            'range_ctrl_high': profile.range_ctrl_high,
            'range_ctrl_normal_low': profile.range_ctrl_normal_low,
            'range_ctrl_normal_high': profile.range_ctrl_normal_high,
            'formula': profile.formula
        }, 200

    @profile_ns.expect(profile_model)
    @profile_ns.response(200, 'Profile updated successfully')
    @profile_ns.response(404, 'Profile not found')
    def put(self, id):
        """Update profile information"""
        profile = Profile.query.get_or_404(id)
        data = request.get_json()
        try:
            for key, value in data.items():
                setattr(profile, key, value)
            db.session.commit()
            return {'message': 'Profile updated successfully'}, 200
        except Exception as e:
            db.session.rollback()
            abort(500, description=str(e))

    @profile_ns.response(200, 'Profile deleted successfully')
    @profile_ns.response(404, 'Profile not found')
    def delete(self, id):
        """Delete a profile"""
        profile = Profile.query.get_or_404(id)
        try:
            db.session.delete(profile)
            db.session.commit()
            return {'message': 'Profile deleted successfully'}, 200
        except Exception as e:
            db.session.rollback()
            abort(500, description=str(e))
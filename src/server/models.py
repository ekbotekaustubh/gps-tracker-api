# project/server/models.py

import jwt
import datetime

from sqlalchemy.dialects.mysql import LONGTEXT
from src.server import app, db, bcrypt

import datetime

user_groups = db.Table('user_groups',
                    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
                    db.Column('group_id', db.Integer, db.ForeignKey('ugroups.id'))
                    )

class UGroup(db.Model):
    """
    User Group Model for storing user groups
    """
    __tablename__ = 'ugroups'
#    __table_args__ = {'mysql_engine':'InnoDB', 'mysql_charset':'utf8','mysql_collate':'utf8_czech_ci'}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    created_on = db.Column(db.DateTime, nullable=False)

    def __init__(self, groupname):
        self.name = groupname
        self.created_on = datetime.datetime.utcnow()

class User(db.Model):
    """ User Model for storing user related details """
    __tablename__ = "users"
#    __table_args__ = {'mysql_engine':'InnoDB', 'mysql_charset':'utf8'}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fname = db.Column(db.String(255), nullable=False)
    lname = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    createOn = db.Column(db.DateTime, nullable=False)
    createBy = db.Column(db.Integer, nullable=True)
    admin = db.Column(db.Boolean, nullable=False, default=False)
    groups = db.relationship('UGroup', secondary=user_groups, backref='users')

    def __init__(self, fname, lname, createdBy, email, password, admin=False):
        self.email = email
        self.password = bcrypt.generate_password_hash(
            password, app.config.get('BCRYPT_LOG_ROUNDS')
        ).decode()
        self.fname = fname
        self.lname = lname
        self.createdBy = createdBy
        self.createOn = datetime.datetime.utcnow()
        self.admin = admin

    def encode_auth_token(self, user_id):
        """
        Generates the Auth Token
        :return: string
        """
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1),
                'iat': datetime.datetime.utcnow(),
                'sub': user_id
            }
            return jwt.encode(
                payload,
                app.config.get('SECRET_KEY'),
                algorithm='HS256'
            )
        except Exception as e:
            return e

    @staticmethod
    def decode_auth_token(auth_token):
        """
        Validates the auth token
        :param auth_token:
        :return: integer|string
        """
        try:
            payload = jwt.decode(auth_token, app.config.get('SECRET_KEY'), algorithms=['HS256'])
            is_blacklisted_token = BlacklistToken.check_blacklist(auth_token)
            if is_blacklisted_token:
                return 'Token blacklisted. Please log in again.'
            else:
                if(isinstance(payload['sub'], int)):
                    return payload['sub']
                else:
                    return 'Invalid token'
        except jwt.ExpiredSignatureError:
            return 'Signature expired. Please log in again.'
        except jwt.InvalidTokenError as e:
            return 'Invalid token ({}). Please log in again.'.format(e)

class BlacklistToken(db.Model):
    """
    Token Model for storing JWT tokens
    """
    __tablename__ = 'blacklist_tokens'
#    __table_args__ = {'mysql_engine':'InnoDB', 'mysql_charset':'utf8'}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    token = db.Column(db.String(500),nullable=False)
    blacklisted_on = db.Column(db.DateTime, nullable=False)

    def __init__(self, token):
        self.token = token
        self.blacklisted_on = datetime.datetime.utcnow()

    def __repr__(self):
        return '<id: token: {}'.format(self.token)
    
    @staticmethod
    def decode_auth_token(auth_token):
        """
        Validates the auth token
        :param auth_token:
        :return: integer|string
        """
        try:
            payload = jwt.decode(auth_token, app.config.get('SECRET_KEY'))
            is_blacklisted_token = BlacklistToken.check_blacklist(auth_token)
            if is_blacklisted_token:
                return 'Token blacklisted. Please log in again.'
            else:
                return payload['sub']
        except jwt.ExpiredSignatureError:
            return 'Signature expired. Please log in again.'
        except jwt.InvalidTokenError:
            return 'Invalid token. Please log in again.'


    @staticmethod
    def check_blacklist(auth_token):
        # check whether auth token has been blacklisted
        res = BlacklistToken.query.filter_by(token=str(auth_token)).first()
        if res:
            return True
        else:
            return False

class Patient(db.Model):
    """
    Patient Model for storing patient related details
    """
    __tablename__ = "patients"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    sname = db.Column(db.String(255), nullable=False)
    aadhar = db.Column(db.String(255), nullable=True)
    email = db.Column(db.String(255), nullable=True)
    mobile = db.Column(db.String(255), nullable=True)
    nation_id = db.Column(db.String(255), nullable=True)
    date = db.Column(db.DateTime, nullable=False)
    patient_type = db.Column(db.String(255), nullable=False)
    age_group = db.Column(db.String(255), nullable=True)
    date_of_birth = db.Column(db.DateTime, nullable=True)
    age = db.Column(db.Integer, nullable=True)
    gender = db.Column(db.String(255), nullable=True)
    reference = db.Column(db.String(255), nullable=True)
    id_address = db.Column(db.String(255), nullable=True)

    def __init__(self, name, sname, date, patient_type, **kwargs):
        self.name = name
        self.sname = sname
        self.date = date
        self.patient_type = patient_type
        # Set optional fields if provided
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)


################################################################################################################################################

# Junction table for many-to-many relationship between Profile and Test
profile_tests = db.Table('profile_tests',
    db.Column('profile_id', db.Integer, db.ForeignKey('profiles.id')),
    db.Column('test_id', db.Integer, db.ForeignKey('tests.id'))
)

package_tests = db.Table('package_tests',
    db.Column('package_id', db.Integer, db.ForeignKey('packages.id')),
    db.Column('test_id', db.Integer, db.ForeignKey('tests.id'))
)

today_tests = db.Table('today_tests',
    db.Column('today_id', db.Integer, db.ForeignKey('today.id')),
    db.Column('test_id', db.Integer, db.ForeignKey('tests.id')),
    db.Column('result', db.String(20), nullable=True)
)

department_analysers = db.Table('department_analysers',
    db.Column('department_id', db.Integer, db.ForeignKey('departments.id')),
    db.Column('analyser_id', db.Integer, db.ForeignKey('analysers.id'))
)

# Test Model
class Test(db.Model):
    __tablename__ = "tests"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(15), nullable=False)
    analyser = db.Column(db.String(15), nullable=True)
    worklist = db.Column(db.String(15), nullable=True)
    company_name = db.Column(db.String(15), nullable=True)
    price = db.Column(db.Float, nullable=True)
    range_infant_low = db.Column(db.Float, nullable=True)
    range_infant_high = db.Column(db.Float, nullable=True)
    range_7y_low = db.Column(db.Float, nullable=True)
    range_7y_high = db.Column(db.Float, nullable=True)
    range_12y_low = db.Column(db.Float, nullable=True)
    range_12y_high = db.Column(db.Float, nullable=True)
    range_adult_low = db.Column(db.Float, nullable=True)
    range_adult_high = db.Column(db.Float, nullable=True)
    type = db.Column(db.String(15), nullable=True)
    gender = db.Column(db.String(15), nullable=True)
    cntrl_range_selection = db.Column(db.Boolean, nullable=True, default=False)
    range_ctrl_low = db.Column(db.Float, nullable=True)
    range_ctrl_high = db.Column(db.Float, nullable=True)
    range_ctrl_normal_low = db.Column(db.Float, nullable=True)
    range_ctrl_normal_high = db.Column(db.Float, nullable=True)
    department = db.Column(db.String(15), nullable=True)
    unit = db.Column(db.String(15), nullable=True)
    formula = db.Column(db.String(255), nullable=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('profiles.id'), nullable=True)
    # One-to-many relationship with Profile
    profile = db.relationship('Profile', backref='test_instance', foreign_keys=[profile_id])

    def __init__(self, name, analyser=None, worklist=None, company_name=None, price=None,
                 range_infant_low=None, range_infant_high=None, range_7y_low=None,
                 range_7y_high=None, range_12y_low=None, range_12y_high=None,
                 range_adult_low=None, range_adult_high=None, type=None, gender=None,
                 cntrl_range_selection=None, range_ctrl_low=None, range_ctrl_high=None,
                 range_ctrl_normal_low=None, range_ctrl_normal_high=None, department=None,
                 unit=None, formula=None, profile_id=None):
        self.name = name
        self.analyser = analyser
        self.worklist = worklist
        self.company_name = company_name
        self.price = price
        self.range_infant_low = range_infant_low
        self.range_infant_high = range_infant_high
        self.range_7y_low = range_7y_low
        self.range_7y_high = range_7y_high
        self.range_12y_low = range_12y_low
        self.range_12y_high = range_12y_high
        self.range_adult_low = range_adult_low
        self.range_adult_high = range_adult_high
        self.type = type
        self.gender = gender
        self.cntrl_range_selection = cntrl_range_selection
        self.range_ctrl_low = range_ctrl_low
        self.range_ctrl_high = range_ctrl_high
        self.range_ctrl_normal_low = range_ctrl_normal_low
        self.range_ctrl_normal_high = range_ctrl_normal_high
        self.department = department
        self.unit = unit
        self.formula = formula if formula else f'calculator + {name}'
        self.profile_id = profile_id

# Profile Model
class Profile(db.Model):
    __tablename__ = "profiles"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    work_prof = db.Column(db.String(15), nullable=True)
    no_of_wklist = db.Column(db.Integer, nullable=True)
    worklist = db.Column(db.String(15), nullable=True)
    price = db.Column(db.Float, nullable=True)
    range_male_low = db.Column(db.Float, nullable=True)
    range_male_high = db.Column(db.Float, nullable=True)
    range_female_low = db.Column(db.Float, nullable=True)
    range_female_high = db.Column(db.Float, nullable=True)
    range_child_low = db.Column(db.Float, nullable=True)
    range_child_high = db.Column(db.Float, nullable=True)
    gender = db.Column(db.String(15), nullable=True)
    cntrl_range_selection = db.Column(db.Boolean, nullable=True, default=False)
    range_ctrl_low = db.Column(db.Float, nullable=True)
    range_ctrl_high = db.Column(db.Float, nullable=True)
    range_ctrl_normal_low = db.Column(db.Float, nullable=True)
    range_ctrl_normal_high = db.Column(db.Float, nullable=True)
    formula = db.Column(db.String(255), nullable=True)
    # Many-to-many relationship with Test
    test_associations = db.relationship('Test', secondary=profile_tests, backref='profile_associations', lazy='dynamic')

    def __init__(self, work_prof=None, no_of_wklist=None, worklist=None, price=None,
                 range_male_low=None, range_male_high=None, range_female_low=None,
                 range_female_high=None, range_child_low=None, range_child_high=None,
                 gender=None, cntrl_range_selection=None, range_ctrl_low=None,
                 range_ctrl_high=None, range_ctrl_normal_low=None,
                 range_ctrl_normal_high=None, formula=None):
        self.work_prof = work_prof
        self.no_of_wklist = no_of_wklist
        self.worklist = worklist
        self.price = price
        self.range_male_low = range_male_low
        self.range_male_high = range_male_high
        self.range_female_low = range_female_low
        self.range_female_high = range_female_high
        self.range_child_low = range_child_low
        self.range_child_high = range_child_high
        self.gender = gender
        self.cntrl_range_selection = cntrl_range_selection
        self.range_ctrl_low = range_ctrl_low
        self.range_ctrl_high = range_ctrl_high
        self.range_ctrl_normal_low = range_ctrl_normal_low
        self.range_ctrl_normal_high = range_ctrl_normal_high
        self.formula = formula if formula else f'calculator + {work_prof or "profile"}'

# Department Model
class Department(db.Model):
    __tablename__ = "departments"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(15), nullable=True)
    hod_name = db.Column(db.String(15), nullable=True)
    mobile = db.Column(db.String(15), nullable=True)
    no_of_analyser = db.Column(db.Integer, nullable=True)
    analysers = db.relationship('Analyser', backref='department', lazy=True)

    def __init__(self, name=None, hod_name=None, mobile=None, no_of_analyser=None):
        self.name = name
        self.hod_name = hod_name
        self.mobile = mobile
        self.no_of_analyser = no_of_analyser

# Analyser Model
class Analyser(db.Model):
    __tablename__ = "analysers"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(15), nullable=True)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=True)

    def __init__(self, name=None, department_id=None):
        self.name = name
        self.department_id = department_id

# Package Model
class Package(db.Model):
    __tablename__ = "packages"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    workprof = db.Column(db.String(15), nullable=True)
    no_of_wklist = db.Column(db.Integer, nullable=True)
    worklist = db.Column(db.String(15), nullable=True)
    price = db.Column(db.Float, nullable=True)
    formula = db.Column(db.String(255), nullable=True)

    def __init__(self, workprof=None, no_of_wklist=None, worklist=None, price=None, formula=None):
        self.workprof = workprof
        self.no_of_wklist = no_of_wklist
        self.worklist = worklist
        self.price = price
        self.formula = formula if formula else f'calculator + {workprof or "package"}'

class Purchase(db.Model):
    __tablename__ = "purchases"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    unique_test = db.Column(db.String(255), nullable=False)
    company_na = db.Column(db.String(255), nullable=True)
    price = db.Column(db.Float, nullable=True)
    volume_r1 = db.Column(db.Float, nullable=True)
    volume_r2 = db.Column(db.Float, nullable=True)
    volume_r3 = db.Column(db.Float, nullable=True)
    no_of_test = db.Column(db.Float, nullable=True)

    def __init__(self, unique_test, company_na=None, price=None, volume_r1=None, 
                 volume_r2=None, volume_r3=None, no_of_test=None):
        self.unique_test = unique_test
        self.company_na = company_na
        self.price = price
        self.volume_r1 = volume_r1
        self.volume_r2 = volume_r2
        self.volume_r3 = volume_r3
        self.no_of_test = no_of_test

class Today(db.Model):
    __tablename__ = "today"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    unique_id = db.Column(db.String(20), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    sr_no = db.Column(db.Integer, nullable=True)
    name = db.Column(db.String(20), nullable=False)
    surname = db.Column(db.String(20), nullable=True)
    no_of_test = db.Column(db.Integer, nullable=False)
    test17_res = db.Column(db.String(20), nullable=True)
    test18_res = db.Column(db.String(20), nullable=True)
    test19_res = db.Column(db.String(20), nullable=True)
    no_of_profile = db.Column(db.Integer, nullable=True)
    workprof = db.Column(db.String(20), nullable=True)
    res = db.Column(db.String(20), nullable=True)
    tests = db.relationship('Test', secondary=today_tests, backref='today_records')

    def __init__(self, unique_id, date, time, sr_no, name, surname, no_of_test, 
                 test17_res=None, test18_res=None, test19_res=None, no_of_profile=None, 
                 workprof=None, res=None):
        self.unique_id = unique_id
        self.date = date
        self.time = time
        self.sr_no = sr_no
        self.name = name
        self.surname = surname
        self.no_of_test = no_of_test
        self.test17_res = test17_res
        self.test18_res = test18_res
        self.test19_res = test19_res
        self.no_of_profile = no_of_profile
        self.workprof = workprof
        self.res = res

class Consume(db.Model):
    __tablename__ = "consume"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date = db.Column(db.Date, nullable=False)
    test_id = db.Column(db.Integer, db.ForeignKey('tests.id'), nullable=False)
    company = db.Column(db.String(255), nullable=False)
    no_of_tests_per_day = db.Column(db.Integer, nullable=False)
    test = db.relationship('Test', backref='consumptions')

    def __init__(self, date, test_id, company, no_of_tests_per_day):
        self.date = date
        self.test_id = test_id
        self.company = company
        self.no_of_tests_per_day = no_of_tests_per_day

class Result(db.Model):
    __tablename__ = "results"
    id = db.Column(db.String(20), primary_key=True)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    group = db.Column(db.String(20), nullable=True)
    test = db.Column(db.String(10), nullable=False)
    result = db.Column(db.String(15), nullable=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('profiles.id'), nullable=True)
    profile_res = db.Column(db.String(10), nullable=True)
    printed = db.Column(db.Integer, nullable=True)
    y_n = db.Column(db.Boolean, nullable=True)
    extra = db.Column(db.String(20), nullable=True)
    profile = db.relationship('Profile', backref='results')

    def __init__(self, id, date, time, test, group=None, result=None, profile_id=None, 
                 profile_res=None, printed=None, y_n=None, extra=None):
        self.id = id
        self.date = date
        self.time = time
        self.group = group
        self.test = test
        self.result = result
        self.profile_id = profile_id
        self.profile_res = profile_res
        self.printed = printed
        self.y_n = y_n
        self.extra = extra

class Control(db.Model):
    """ Control Model for storing test control details """
    __tablename__ = "controls"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # Auto-incrementing ID
    date = db.Column(db.Date, nullable=False)  # date
    analyser = db.Column(db.String(15), nullable=False)  # analysers (alpha)
    test_name = db.Column(db.String(15), nullable=False)  # testname (alpha)
    control_completed = db.Column(db.Boolean, nullable=True)  # cntrlcomp (logical)
    range_low = db.Column(db.Float, nullable=True)  # range low (float)
    low_y_n = db.Column(db.Boolean, nullable=True)  # low Y/n (logical)
    range_norm_high = db.Column(db.Float, nullable=True)  # Range Norm high (float)
    range_norm_low = db.Column(db.Float, nullable=True)  # Range Norm low (float)
    norm_y_n = db.Column(db.Boolean, nullable=True)  # Norm Y/n (logical)
    range_high = db.Column(db.Float, nullable=True)  # Range high (float)
    high_y_n = db.Column(db.Boolean, nullable=True)  # high Y/n (logical)

    def __init__(self, date, analyser, test_name, control_completed=None, range_low=None, 
                 low_y_n=None, range_norm_high=None, range_norm_low=None, norm_y_n=None, 
                 range_high=None, high_y_n=None):
        self.date = date
        self.analyser = analyser
        self.test_name = test_name
        self.control_completed = control_completed
        self.range_low = range_low
        self.low_y_n = low_y_n
        self.range_norm_high = range_norm_high
        self.range_norm_low = range_norm_low
        self.norm_y_n = norm_y_n
        self.range_high = range_high
        self.high_y_n = high_y_n

# Association tables
patient_work_prof = db.Table('patient_work_prof',
    db.Column('patient_id', db.Integer, db.ForeignKey('patient_data_entries.id')),
    db.Column('profile_id', db.Integer, db.ForeignKey('profiles.id'))
)

patient_work_list = db.Table('patient_work_list',
    db.Column('patient_id', db.Integer, db.ForeignKey('patient_data_entries.id')),
    db.Column('package_id', db.Integer, db.ForeignKey('packages.id'))
)

patient_task_list = db.Table('patient_task_list',
    db.Column('patient_id', db.Integer, db.ForeignKey('patient_data_entries.id')),
    db.Column('test_id', db.Integer, db.ForeignKey('tests.id'))
)

class PatientDataEntry(db.Model):
    __tablename__ = 'patient_data_entries'
    id = db.Column(db.Integer, primary_key=True)
    ref = db.Column(db.String(255))
    today_date = db.Column(db.DateTime)
    id_name = db.Column(db.String(255))
    id_value = db.Column(db.String(255))
    gender = db.Column(db.String(50))
    dob = db.Column(db.DateTime)
    age = db.Column(db.String(50))
    mobile = db.Column(db.String(20))
    address = db.Column(db.String(255))
    aadhar = db.Column(db.String(20))
    national_id = db.Column(db.String(20))

    # Many-to-many relationships
    work_profs = db.relationship('Profile', secondary=patient_work_prof, backref=db.backref('patient_entries', lazy='dynamic'))
    work_lists = db.relationship('Package', secondary=patient_work_list, backref=db.backref('patient_entries', lazy='dynamic'))
    task_lists = db.relationship('Test', secondary=patient_task_list, backref=db.backref('patient_entries', lazy='dynamic'))

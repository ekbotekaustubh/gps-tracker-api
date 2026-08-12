# project/tests/base.py


from flask_testing import TestCase

from src.server import app, db


class BaseTestCase(TestCase):
    """ Base Tests """

    def create_app(self):
        app.config.from_object('src.server.config.TestingConfig')
        return app

    def setUp(self):
        db.create_all()
        
        # Seed country, state, role, org, branch to satisfy foreign key constraints
        from src.server.models.country import Country
        from src.server.models.state import State
        from src.server.models.role import Role
        from src.server.models.organization import Organization
        from src.server.models.branch import Branch

        country = Country(name='India', country_code='IN')
        db.session.add(country)
        db.session.flush()

        state = State(name='Maharashtra', state_code='MH', country_id=country.id)
        db.session.add(state)
        db.session.flush()

        role = Role(name='Super User', status=1)
        db.session.add(role)
        db.session.flush()

        org = Organization(
        name='Test Org',
        address_line_1='Test Address',
        address_line_2='',
        city='Mumbai',
        pincode='400001',
        country_id=country.id,
        state_id=state.id,
        status=True
    )

        db.session.add(org)
        db.session.flush()

        branch = Branch(
            org_id=org.id,
            name='Test Branch',
            address_line_1='Address',
            city='Mumbai',
            pincode='400001',
            country_id=country.id,
            state_id=state.id,
            mobile='9876543210',
            status=1
        )
        db.session.add(branch)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

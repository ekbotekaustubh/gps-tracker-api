# src/tests/test_states.py

import unittest
from src.tests.base import BaseTestCase
from src.server import db
from src.server.models import Country, State


class TestStatesAPI(BaseTestCase):
    """Test cases for States API endpoints"""

    def test_get_states_by_country_id(self):
        """Test retrieving states of a specific country by ID"""
        # Retrieve the seeded country
        country = Country.query.first()
        self.assertIsNotNone(country)

        # Create additional test states for this country
        state = State(name='Karnataka', state_code='KA', country_id=country.id)
        db.session.add(state)
        db.session.commit()

        # Make request
        response = self.client.get(f'/api/v1/states/{country.id}')

        # Assertions
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['status'], 'success')
        
        # Verify that we retrieve at least the seeded state and our new state
        self.assertGreaterEqual(len(data['data']), 2)
        
        # Verify structure
        state_data = data['data'][0]
        self.assertIn('id', state_data)
        self.assertEqual(state_data['country_id'], country.id)
        self.assertIn('name', state_data)
        self.assertIn('state_code', state_data)
        self.assertIn('created_at', state_data)
        self.assertIn('updated_at', state_data)

    def test_get_states_by_invalid_country_id(self):
        """Test retrieving states of a non-existent country"""
        response = self.client.get('/api/v1/states/999999')
        self.assertEqual(response.status_code, 404)
        data = response.get_json()
        self.assertEqual(data['status'], 'fail')
        self.assertEqual(data['message'], 'Country not found.')


if __name__ == '__main__':
    unittest.main()

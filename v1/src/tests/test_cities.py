# src/tests/test_cities.py

import unittest
from src.tests.base import BaseTestCase
from src.server import db
from src.server.models import State, City


class TestCitiesAPI(BaseTestCase):
    """Test cases for Cities API endpoints"""

    def test_get_cities_by_state_id(self):
        """Test retrieving cities of a specific state by ID"""
        # Retrieve the seeded state
        state = State.query.first()
        self.assertIsNotNone(state)

        # Create additional test cities for this state
        city = City(name='Pune', state_id=state.id, country_id=state.country_id)
        db.session.add(city)
        db.session.commit()

        # Make request
        response = self.client.get(f'/api/v1/cities/{state.id}')

        # Assertions
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['status'], 'success')
        
        # Verify that we retrieve the new city
        self.assertGreaterEqual(len(data['data']), 1)
        
        # Verify structure
        city_data = data['data'][0]
        self.assertIn('id', city_data)
        self.assertEqual(city_data['state_id'], state.id)
        self.assertEqual(city_data['country_id'], state.country_id)
        self.assertIn('name', city_data)
        self.assertIn('created_at', city_data)
        self.assertIn('updated_at', city_data)

    def test_get_cities_by_invalid_state_id(self):
        """Test retrieving cities of a non-existent state"""
        response = self.client.get('/api/v1/cities/999999')
        self.assertEqual(response.status_code, 404)
        data = response.get_json()
        self.assertEqual(data['status'], 'fail')
        self.assertEqual(data['message'], 'State not found.')


if __name__ == '__main__':
    unittest.main()

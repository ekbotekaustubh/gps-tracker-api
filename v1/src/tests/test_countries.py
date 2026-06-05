# src/tests/test_countries.py

import unittest
from src.tests.base import BaseTestCase
from src.server import db
from src.server.models import Country


class TestCountriesAPI(BaseTestCase):
    """Test cases for Countries API endpoints"""

    def test_get_all_countries(self):
        """Test retrieving all countries"""
        # Create test countries
        country1 = Country(name='India', country_code='IN')
        country2 = Country(name='United States', country_code='US')
        db.session.add(country1)
        db.session.add(country2)
        db.session.commit()

        # Make request
        response = self.client.get('/api/v1/countries')
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['status'], 'success')
        self.assertGreaterEqual(len(data['data']), 2)
        
        # Verify response structure
        self.assertIn('message', data)
        self.assertIsInstance(data['data'], list)
        
        # Verify data contains expected fields
        country = data['data'][0]
        self.assertIn('id', country)
        self.assertIn('name', country)
        self.assertIn('country_code', country)
        self.assertIn('created_at', country)
        self.assertIn('updated_at', country)

    def test_get_country_by_id(self):
        """Test retrieving a specific country by ID"""
        # Create test country
        country = Country(name='India', country_code='IN')
        db.session.add(country)
        db.session.commit()

        # Make request
        response = self.client.get(f'/api/v1/countries/{country.id}')
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['data']['id'], country.id)
        self.assertEqual(data['data']['name'], 'India')
        self.assertEqual(data['data']['country_code'], 'IN')

    def test_get_country_by_invalid_id(self):
        """Test retrieving a non-existent country"""
        # Make request with invalid ID
        response = self.client.get('/api/v1/countries/999999')
        
        # Assertions
        self.assertEqual(response.status_code, 404)
        data = response.get_json()
        self.assertEqual(data['status'], 'fail')
        self.assertEqual(data['message'], 'Country not found.')

    def test_get_empty_countries_list(self):
        """Test retrieving countries when no countries exist"""
        # Make request with empty database
        response = self.client.get('/api/v1/countries')
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(len(data['data']), 0)


if __name__ == '__main__':
    unittest.main()

# src/tests/test_organization.py

import json
import unittest

from src.tests.base import BaseTestCase


class TestOrganizationAPI(BaseTestCase):
    """Test cases for Organization API"""

    def test_create_organization(self):
        """Test organization creation"""

        response = self.client.post(
            "/api/v1/organizations",
            data=json.dumps({
                "name": "Test Organization",
                "address_line_1": "Pune",
                "address_line_2": "",
                "city": "Pune",
                "pincode": "411001",
                "country_id": 1,
                "state_id": 1,
                "status": True
            }),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 201)

    def test_get_organization_list(self):
        """Test get all organizations"""

        response = self.client.get("/api/v1/organizations")

        self.assertEqual(response.status_code, 200)

    def test_get_organization_by_id(self):
        """Test get organization by ID"""

        response = self.client.get("/api/v1/organizations/1")

        self.assertIn(response.status_code, [200, 404])

    def test_get_organization_by_name(self):
        """Test get organization by name"""

        response = self.client.get(
            "/api/v1/organizations?name=Test Organization"
        )

        self.assertIn(response.status_code, [200, 404])

    def test_update_organization(self):
        """Test update organization"""

        response = self.client.put(
            "/api/v1/organizations/1",
            data=json.dumps({
                "name": "Updated Organization",
                "address_line_1": "Mumbai",
                "address_line_2": "",
                "city": "Mumbai",
                "pincode": "400001",
                "country_id": 1,
                "state_id": 1,
                "status": True
            }),
            content_type="application/json"
        )

        self.assertIn(response.status_code, [200, 404])

    def test_delete_organization(self):
        """Test delete organization"""

        response = self.client.delete("/api/v1/organizations/1")

        self.assertIn(response.status_code, [200, 404])


if __name__ == "__main__":
    unittest.main()
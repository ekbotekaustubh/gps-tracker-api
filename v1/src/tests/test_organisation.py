# src/tests/test_organizations.py

import json
import unittest

from src.tests.base import BaseTestCase
from src.server import db
from src.server.models import Country, State, Organization


TEST_ORGANISATION = {
    "name": "Tata Technologies",
    "address_line_1": "Hinjewadi Phase 1",
    "address_line_2": "Rajiv Gandhi Infotech Park",
    "city": "Pune",
    "pincode": "411057",
    "country_id": 1,
    "state_id": 1,
    "status": True
}


class TestOrganisationAPI(BaseTestCase):
    """Test cases for Organisation API endpoints"""

    def create_organisation(self):
        return self.client.post(
            "/api/v1/organizations",
            data=json.dumps(TEST_ORGANISATION),
            content_type="application/json"
        )

    def test_create_organisation(self):
        """Test organisation creation"""

        response = self.create_organisation()

        self.assertEqual(response.status_code, 201)

        data = response.get_json()

        self.assertEqual(data["status"], "success")
        self.assertEqual(
            data["message"],
            "Organisation added successfully."
        )

    def test_duplicate_organisation(self):
        """Test duplicate organisation"""

        self.create_organisation()

        response = self.create_organisation()

        self.assertEqual(response.status_code, 409)

        data = response.get_json()

        self.assertEqual(data["status"], "fail")
        self.assertEqual(
            data["message"],
            "Organisation already exists."
        )

    def test_get_organisation_list(self):
        """Test get organisation list"""

        self.create_organisation()

        response = self.client.get("/api/v1/organizations")

        self.assertEqual(response.status_code, 200)

        data = response.get_json()

        self.assertEqual(data["status"], "success")
        self.assertGreaterEqual(len(data["data"]), 1)

    def test_get_organisation_by_name(self):
        """Test get organisation by name"""

        self.create_organisation()

        response = self.client.get(
            "/api/v1/organizations?name=Tata Technologies"
        )

        self.assertEqual(response.status_code, 200)

        data = response.get_json()

        self.assertEqual(data["status"], "success")
        self.assertEqual(
            data["data"]["name"],
            "Tata Technologies"
        )

    def test_get_organisation_by_invalid_name(self):
        """Test invalid organisation name"""

        response = self.client.get(
            "/api/v1/organizations?name=XYZ"
        )

        self.assertEqual(response.status_code, 404)

        data = response.get_json()

        self.assertEqual(data["status"], "fail")
        self.assertEqual(
            data["message"],
            "Organisation not found."
        )

    def test_get_organisation_by_id(self):
        """Test get organisation by ID"""

        self.create_organisation()

        organisation = Organization.query.filter_by(
            name="Tata Technologies"
        ).first()

        response = self.client.get(
            f"/api/v1/organizations/{organisation.id}"
        )

        self.assertEqual(response.status_code, 200)

        data = response.get_json()

        self.assertEqual(data["status"], "success")
        self.assertEqual(
            data["data"]["id"],
            organisation.id
        )

    def test_get_invalid_organisation(self):
        """Test invalid organisation ID"""

        response = self.client.get(
            "/api/v1/organizations/999999"
        )

        self.assertEqual(response.status_code, 404)

        data = response.get_json()

        self.assertEqual(data["status"], "fail")
        self.assertEqual(
            data["message"],
            "Organisation not found."
        )

    def test_update_organisation(self):
        """Test update organisation"""

        self.create_organisation()

        organisation = Organization.query.filter_by(
            name="Tata Technologies"
        ).first()

        update_data = TEST_ORGANISATION.copy()
        update_data["name"] = "Infosys"

        response = self.client.put(
            f"/api/v1/organizations/{organisation.id}",
            data=json.dumps(update_data),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 200)

        data = response.get_json()

        self.assertEqual(data["status"], "success")
        self.assertEqual(
            data["message"],
            "Organisation updated successfully."
        )

    def test_delete_organisation(self):
        """Test delete organisation"""

        self.create_organisation()

        organisation = Organization.query.filter_by(
            name="Tata Technologies"
        ).first()

        response = self.client.delete(
            f"/api/v1/organizations/{organisation.id}"
        )

        self.assertEqual(response.status_code, 200)

        data = response.get_json()

        self.assertEqual(data["status"], "success")
        self.assertEqual(
            data["message"],
            "Organisation deleted successfully."
        )


if __name__ == "__main__":
    unittest.main()
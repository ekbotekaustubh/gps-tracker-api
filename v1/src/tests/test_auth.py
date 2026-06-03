# src/tests/test_auth.py


import time
import json
import unittest

from src.server import db
from src.server.models import User, BlacklistToken
from src.tests.base import BaseTestCase


# Default test user data matching the current User model constructor
TEST_USER = {
    'name': 'Joe Test',
    'email': 'joe@gmail.com',
    'mobile': '9876543210',
    'branch_id': 0,
    'role_id': 1,
    'country_id': 1,
    'state_id': 1,
    'username': 'joetest',
    'password': '123456',
}

TEST_USER_2 = {
    'name': 'Jane Test',
    'email': 'jane@gmail.com',
    'mobile': '9876543211',
    'branch_id': 0,
    'role_id': 1,
    'country_id': 1,
    'state_id': 1,
    'username': 'janetest',
    'password': '654321',
}


def register_user(self, user_data=None):
    """Register a user via the API endpoint."""
    data = user_data or TEST_USER
    return self.client.post(
        '/api/v1/auth/register',
        data=json.dumps(data),
        content_type='application/json',
    )


def login_user(self, username, password):
    """Login a user via the API endpoint."""
    return self.client.post(
        '/api/v1/auth/login',
        data=json.dumps(dict(
            username=username,
            password=password
        )),
        content_type='application/json',
    )


class TestAuthBlueprint(BaseTestCase):

    def test_registration(self):
        """ Test for user registration """
        with self.client:
            response = register_user(self)
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'success')
            self.assertTrue(data['message'] == 'Successfully registered.')
            self.assertTrue(data['auth_token'])
            self.assertTrue(response.content_type == 'application/json')
            self.assertEqual(response.status_code, 201)

    def test_registered_with_already_registered_user(self):
        """ Test registration with already registered username"""
        with self.client:
            # Register first
            register_user(self)
            # Try registering again with same data
            response = register_user(self)
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(
                data['message'] == 'User already exists. Please Log in.')
            self.assertTrue(response.content_type == 'application/json')
            self.assertEqual(response.status_code, 202)

    def test_registered_with_already_registered_email(self):
        """ Test registration with already registered email but different username"""
        with self.client:
            # Register first user
            register_user(self)
            # Try registering with same email but different username
            duplicate_email_user = TEST_USER.copy()
            duplicate_email_user['username'] = 'differentuser'
            response = register_user(self, duplicate_email_user)
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(
                data['message'] == 'User with this email already exists. Please Log in.')
            self.assertEqual(response.status_code, 202)

    def test_registered_user_login(self):
        """ Test for login of registered-user login """
        with self.client:
            # user registration
            resp_register = register_user(self)
            data_register = json.loads(resp_register.data.decode())
            self.assertTrue(data_register['status'] == 'success')
            self.assertTrue(
                data_register['message'] == 'Successfully registered.'
            )
            self.assertTrue(data_register['auth_token'])
            self.assertTrue(resp_register.content_type == 'application/json')
            self.assertEqual(resp_register.status_code, 201)
            # registered user login
            response = login_user(self, TEST_USER['username'], TEST_USER['password'])
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'success')
            self.assertTrue(data['message'] == 'Successfully logged in.')
            self.assertTrue(data['auth_token'])
            self.assertTrue(response.content_type == 'application/json')
            self.assertEqual(response.status_code, 200)

    def test_non_registered_user_login(self):
        """ Test for login of non-registered user """
        with self.client:
            response = login_user(self, 'nobody', '123456')
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(data['message'] == 'User does not exist or invalid credentials.')
            self.assertTrue(response.content_type == 'application/json')
            self.assertEqual(response.status_code, 404)

    def test_user_status(self):
        """ Test for user status """
        with self.client:
            resp_register = register_user(self)
            auth_token = json.loads(resp_register.data.decode())['auth_token']
            response = self.client.get(
                '/api/v1/auth/user',
                headers=dict(
                    Authorization='Bearer ' + auth_token
                )
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'success')
            self.assertTrue(data['email'] == TEST_USER['email'])
            self.assertTrue(data['username'] == TEST_USER['username'])
            self.assertEqual(response.status_code, 200)

    def test_user_status_malformed_bearer_token(self):
        """ Test for user status with malformed bearer token"""
        with self.client:
            resp_register = register_user(self)
            response = self.client.get(
                '/api/v1/auth/user',
                headers=dict(
                    Authorization='Bearer' + json.loads(
                        resp_register.data.decode()
                    )['auth_token']
                )
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(data['message'] == 'Bearer token malformed.')
            self.assertEqual(response.status_code, 401)

    def test_valid_logout(self):
        """ Test for logout before token expires """
        with self.client:
            # user registration
            resp_register = register_user(self)
            data_register = json.loads(resp_register.data.decode())
            self.assertTrue(data_register['status'] == 'success')
            self.assertEqual(resp_register.status_code, 201)
            # user login
            resp_login = login_user(self, TEST_USER['username'], TEST_USER['password'])
            data_login = json.loads(resp_login.data.decode())
            self.assertTrue(data_login['status'] == 'success')
            self.assertTrue(data_login['auth_token'])
            self.assertEqual(resp_login.status_code, 200)
            # valid token logout
            response = self.client.post(
                '/api/v1/auth/logout',
                headers=dict(
                    Authorization='Bearer ' + data_login['auth_token']
                )
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'success')
            self.assertTrue(data['message'] == 'Successfully logged out.')
            self.assertEqual(response.status_code, 200)

    def test_invalid_logout(self):
        """ Testing logout after the token expires """
        with self.client:
            # user registration
            resp_register = register_user(self)
            data_register = json.loads(resp_register.data.decode())
            self.assertTrue(data_register['status'] == 'success')
            self.assertEqual(resp_register.status_code, 201)
            # user login
            resp_login = login_user(self, TEST_USER['username'], TEST_USER['password'])
            data_login = json.loads(resp_login.data.decode())
            self.assertTrue(data_login['status'] == 'success')
            self.assertTrue(data_login['auth_token'])
            self.assertEqual(resp_login.status_code, 200)
            # invalid token logout
            time.sleep(6)
            response = self.client.post(
                '/api/v1/auth/logout',
                headers=dict(
                    Authorization='Bearer ' + data_login['auth_token']
                )
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(
                data['message'] == 'Signature expired. Please log in again.')
            self.assertEqual(response.status_code, 401)

    def test_valid_blacklisted_token_logout(self):
        """ Test for logout after a valid token gets blacklisted """
        with self.client:
            # user registration
            resp_register = register_user(self)
            data_register = json.loads(resp_register.data.decode())
            self.assertTrue(data_register['status'] == 'success')
            self.assertEqual(resp_register.status_code, 201)
            # user login
            resp_login = login_user(self, TEST_USER['username'], TEST_USER['password'])
            data_login = json.loads(resp_login.data.decode())
            self.assertTrue(data_login['status'] == 'success')
            self.assertTrue(data_login['auth_token'])
            self.assertEqual(resp_login.status_code, 200)
            # blacklist a valid token
            blacklist_token = BlacklistToken(
                token=data_login['auth_token'])
            db.session.add(blacklist_token)
            db.session.commit()
            # blacklisted valid token logout
            response = self.client.post(
                '/api/v1/auth/logout',
                headers=dict(
                    Authorization='Bearer ' + data_login['auth_token']
                )
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(data['message'] == 'Token blacklisted. Please log in again.')
            self.assertEqual(response.status_code, 401)

    def test_valid_blacklisted_token_user(self):
        """ Test for user status with a blacklisted valid token """
        with self.client:
            resp_register = register_user(self)
            auth_token = json.loads(resp_register.data.decode())['auth_token']
            # blacklist a valid token
            blacklist_token = BlacklistToken(token=auth_token)
            db.session.add(blacklist_token)
            db.session.commit()
            response = self.client.get(
                '/api/v1/auth/user',
                headers=dict(
                    Authorization='Bearer ' + auth_token
                )
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(data['message'] == 'Token blacklisted. Please log in again.')
            self.assertEqual(response.status_code, 401)


if __name__ == '__main__':
    unittest.main()

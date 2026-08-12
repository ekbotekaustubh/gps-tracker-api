# src/tests/test_user_model.py


import unittest

from src.server import db
from src.server.models import User
from src.tests.base import BaseTestCase


class TestUserModel(BaseTestCase):

    def _create_test_user(self):
        """Helper to create a user with all required fields."""
        user = User(
            name='Test User',
            email='test@test.com',
            mobile='9876543210',
            branch_id=1,
            role_id=1,
            country_id=1,
            state_id=1,
            username='testuser',
            password='test'
        )
        db.session.add(user)
        db.session.commit()
        return user

    def test_encode_auth_token(self):
        user = self._create_test_user()
        auth_token = user.encode_auth_token(user.id)
        self.assertTrue(isinstance(auth_token, str))

    def test_decode_auth_token(self):
        user = self._create_test_user()
        auth_token = user.encode_auth_token(user.id)
        self.assertTrue(isinstance(auth_token, str))
        self.assertTrue(User.decode_auth_token(auth_token) == user.id)

    def test_password_is_hashed(self):
        """Verify that stored password is not plaintext."""
        user = self._create_test_user()
        self.assertNotEqual(user.password, 'test')
        self.assertTrue(user.password.startswith('$2b$'))

    def test_user_repr(self):
        user = self._create_test_user()
        self.assertEqual(repr(user), '<User testuser>')


if __name__ == '__main__':
    unittest.main()

# src/tests/test_config.py


import os
import unittest

from flask import current_app
from flask_testing import TestCase

from src.server import app


class TestDevelopmentConfig(TestCase):
    def create_app(self):
        app.config.from_object('src.server.config.DevelopmentConfig')
        return app

    def test_app_is_development(self):
        self.assertTrue(app.config['DEBUG'] is True)
        self.assertFalse(current_app is None)
        self.assertEqual(app.config['BCRYPT_LOG_ROUNDS'], 4)
        self.assertFalse(app.config['TESTING'])


class TestTestingConfig(TestCase):
    def create_app(self):
        app.config.from_object('src.server.config.TestingConfig')
        return app

    def test_app_is_testing(self):
        self.assertTrue(app.config['DEBUG'])
        self.assertTrue(app.config['TESTING'])
        self.assertEqual(app.config['BCRYPT_LOG_ROUNDS'], 4)
        self.assertEqual(
            app.config['SQLALCHEMY_DATABASE_URI'],
            'sqlite:///:memory:'
        )


class TestProductionConfig_MySQL(TestCase):
    def create_app(self):
        app.config.from_object('src.server.config.ProductionConfig_MySQL')
        return app

    def test_app_is_production_mysql(self):
        self.assertEqual(app.config['BCRYPT_LOG_ROUNDS'], 13)
        self.assertIn('mysql', app.config['SQLALCHEMY_DATABASE_URI'])
        self.assertIn('gps_tracker', app.config['SQLALCHEMY_DATABASE_URI'])


class TestProductionConfig(TestCase):
    def create_app(self):
        app.config.from_object('src.server.config.ProductionConfig')
        return app

    def test_app_is_production(self):
        self.assertTrue(app.config['DEBUG'] is False)
        self.assertEqual(app.config['BCRYPT_LOG_ROUNDS'], 13)


if __name__ == '__main__':
    unittest.main()

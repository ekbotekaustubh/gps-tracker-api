# manage.py

import os
import unittest
import coverage
import click
from flask.cli import FlaskGroup
from flask import Flask
from flask_restx import Api
from src.server import app

COV = coverage.coverage(
    branch=True,
    include='project/*',
    omit=[
        'src/tests/*',
        'src/server/config.py',
        'src/server/*/__init__.py'
    ]
)
COV.start()

from src.server import app, db
from src.server import models  # noqa: F401 — ensures all models are registered with SQLAlchemy

cli = FlaskGroup(app)

@cli.command("test")
def test():
    """Runs the unit tests without test coverage."""
    tests = unittest.TestLoader().discover('project/tests', pattern='test*.py')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        return 0
    return 1

@cli.command("cov")
def cov():
    """Runs the unit tests with coverage."""
    tests = unittest.TestLoader().discover('project/tests')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        COV.stop()
        COV.save()
        print('Coverage Summary:')
        COV.report()
        basedir = os.path.abspath(os.path.dirname(__file__))
        covdir = os.path.join(basedir, 'tmp/coverage')
        COV.html_report(directory=covdir)
        print('HTML version: file://%s/index.html' % covdir)
        COV.erase()
        return 0
    return 1

@cli.command("create_db")
def create_db():
    """Creates the db tables."""
    db.create_all()

@cli.command("drop_db")
def drop_db():
    """Drops the db tables."""
    db.drop_all()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

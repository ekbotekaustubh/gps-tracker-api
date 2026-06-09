# src/server/config.py

import os

basedir = os.path.abspath(os.path.dirname(__file__))
database_name = 'gps_tracker'


class BaseConfig:
    """Base configuration."""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-change-me')
    DEBUG = False
    TESTING = False
    BCRYPT_LOG_ROUNDS = 13
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    @classmethod
    def init_app(cls, app):
        pass


class DevelopmentConfig(BaseConfig):
    """Development configuration."""
    DEBUG = True
    BCRYPT_LOG_ROUNDS = 4
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'mysql+pymysql://root:toor@localhost:3306/gps_tracker'
    )


class TestingConfig(BaseConfig):
    """Testing configuration."""
    DEBUG = True
    TESTING = True
    BCRYPT_LOG_ROUNDS = 4
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    PRESERVE_CONTEXT_ON_EXCEPTION = False


class ProductionConfig_MySQL(BaseConfig):
    """Production configuration (MySQL)."""
    SECRET_KEY = os.environ.get('SECRET_KEY')
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'mysql+pymysql://root:toor@mysql:3306/gps_tracker'
    )

    @classmethod
    def init_app(cls, app):
        if not app.config.get('SECRET_KEY'):
            import warnings
            warnings.warn(
                'SECRET_KEY is not set! Using fallback. '
                'Set the SECRET_KEY environment variable in production.',
                RuntimeWarning
            )
            app.config['SECRET_KEY'] = 'fallback-secret-change-in-production'


class ProductionConfig(BaseConfig):
    """Production configuration (SQLite)."""
    SECRET_KEY = os.environ.get('SECRET_KEY')
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        f'sqlite:///{os.path.join(basedir, "..", "..", "gps_tracker.db")}'
    )

    @classmethod
    def init_app(cls, app):
        if not app.config.get('SECRET_KEY'):
            import warnings
            warnings.warn(
                'SECRET_KEY is not set! Using fallback. '
                'Set the SECRET_KEY environment variable in production.',
                RuntimeWarning
            )
            app.config['SECRET_KEY'] = 'fallback-secret-change-in-production'

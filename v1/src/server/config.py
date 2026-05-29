# project/server/config.py

import os
from urllib.parse import quote  

basedir = os.path.abspath(os.path.dirname(__file__))
# postgres_local_base = 'postgresql://postgres:@localhost/'
database_name = 'gps_tracker'
sqlite_db_base = 'sqlite:///.\\'


class BaseConfig:
    """Base configuration."""
    SECRET_KEY = os.getenv('SECRET_KEY', 'my_precious')
    DEBUG = False
    BCRYPT_LOG_ROUNDS = 13
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(BaseConfig):
    """Development configuration."""
    DEBUG = True
    BCRYPT_LOG_ROUNDS = 4
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', "sqlite:///D:\\clients\\edgelytics\\iotful\\software\\server-template\\mydb.db")


class TestingConfig(BaseConfig):
    """Testing configuration."""
    DEBUG = True
    TESTING = True
    BCRYPT_LOG_ROUNDS = 4
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', "sqlite:///:memory:")
    PRESERVE_CONTEXT_ON_EXCEPTION = False

class ProductionConfig_MySQL(BaseConfig):
    """Production configuration."""
    SECRET_KEY = 'my_precious'
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'mysql+pymysql://root:toor@mysql:3306/gps_tracker')
    #"mysql://s_ac:SerAditiControls\@123@akshaydandekar.in:3306/sac"


class ProductionConfig(BaseConfig):
    """Production configuration."""
    SECRET_KEY = 'my_precious'
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = "sqlite:////opt/server-aditicontrols/mydb.db"

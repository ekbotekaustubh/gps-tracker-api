# src/server/__init__.py

import os

from flask import Flask, jsonify, redirect
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_restx import Api

app = Flask(__name__)

# Configure CORS to allow all origins
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

app_settings = os.getenv(
    'APP_SETTINGS',
    'src.server.config.ProductionConfig_MySQL'
)
app.config.from_object(app_settings)

# Dynamically import and run init_app on config class
try:
    from src.server import config
    config_class_name = app_settings.split('.')[-1]
    config_class = getattr(config, config_class_name)
    if hasattr(config_class, 'init_app'):
        config_class.init_app(app)
except Exception:
    pass

bcrypt = Bcrypt(app)
db = SQLAlchemy(app)

# Health check endpoint
@app.route('/health')
def health_check():
    return jsonify({"status": "healthy"}), 200

# Root redirect to Swagger UI
@app.route('/')
def index():
    return redirect('/docs')

# Define authorizations for Swagger
authorizations = {
    'Bearer Auth': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization',
        'description': 'Enter your bearer token in the format: Bearer <token>'
    }
}

# Initialize Swagger documentation with authorizations
api = Api(
    app,
    version='1.0',
    title='GPS Tracker API',
    description='A Flask API for GPS Tracker Management System',
    doc='/docs',
    prefix='/api/v1',
    default='auth',
    default_label='Authentication Operations',
    authorizations=authorizations
)

# Create namespaces for different modules
auth_ns = api.namespace('auth', description='Authentication operations')
countries_ns = api.namespace('countries', description='Countries operations')

# Import and register auth views (explicit import, not wildcard)
from src.server.auth import views as auth_views  # noqa: E402, F401
from src.server.countries import views as countries_views  # noqa: E402, F401

# Explicitly register all namespaces
api.add_namespace(auth_ns)
api.add_namespace(countries_ns)
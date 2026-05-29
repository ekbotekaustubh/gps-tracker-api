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
    prefix='/backend/api',
    default='auth',
    default_label='Authentication Operations',
    authorizations=authorizations
)

# Create namespaces for different modules
auth_ns = api.namespace('auth', description='Authentication operations')

# Import views after creating namespaces
from src.server.auth.views import *

# Explicitly register all namespaces
api.add_namespace(auth_ns)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
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
    title='Pathology Lab API',
    description='A Flask API for Pathology Lab Management System',
    doc='/docs',
    prefix='/backend/api',
    default='auth',
    default_label='Authentication Operations',
    authorizations=authorizations
)

# Create namespaces for different modules
auth_ns = api.namespace('auth', description='Authentication operations')
patient_ns = api.namespace('patient', description='Patient operations')
profile_ns = api.namespace('profile', description='Profile operations')
test_ns = api.namespace('test', description='Test operations')
package_ns = api.namespace('package', description='Package operations')
purchase_ns = api.namespace('purchase', description='Purchase operations')
today_ns = api.namespace('today', description='Today operations')
department_ns = api.namespace('department', description='Department operations')
consume_ns = api.namespace('consume', description='Consume operations')
result_ns = api.namespace('result', description='Result operations')
control_ns = api.namespace('control', description='Control operations')
patient_data_ns = api.namespace('patient_data', description='Patient data entry operations')

# Import views after creating namespaces
from src.server.auth.views import *
from src.server.patient.views import *
from src.server.profile.views import *
from src.server.tests.views import *
from src.server.package.views import *
from src.server.purchase.views import *
from src.server.today.views import *
from src.server.department.views import *
from src.server.consume.views import *
from src.server.result.views import *
from src.server.control.views import *
from src.server.patient_data.views import *

# Explicitly register all namespaces
api.add_namespace(auth_ns)
api.add_namespace(patient_ns)
api.add_namespace(profile_ns)
api.add_namespace(test_ns)
api.add_namespace(package_ns)
api.add_namespace(purchase_ns)
api.add_namespace(today_ns)
api.add_namespace(department_ns)
api.add_namespace(consume_ns)
api.add_namespace(result_ns)
api.add_namespace(control_ns)
api.add_namespace(patient_data_ns)  # Ensure this is included

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
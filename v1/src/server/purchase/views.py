# project/server/purchase/views.py

from flask import Blueprint, request, make_response, jsonify
from flask.views import MethodView

from src.server import db
from src.server.models import Purchase

purchase_blueprint = Blueprint('purchase', __name__)

class PurchaseAPI(MethodView):
    """
    Purchase Resource for CRUD operations
    """

    def get(self, purchase_id=None):
        """
        Read: Get a single purchase by ID or all purchases if no ID is provided
        """
        try:
            if purchase_id:
                # Get a single purchase
                purchase = Purchase.query.get(purchase_id)
                if not purchase:
                    return make_response(jsonify({
                        'status': 'fail',
                        'message': 'Purchase not found.'
                    })), 404

                # Prepare response
                purchase_data = {
                    'id': purchase.id,
                    'unique_test': purchase.unique_test,
                    'company_na': purchase.company_na,
                    'price': purchase.price,
                    'volume_r1': purchase.volume_r1,
                    'volume_r2': purchase.volume_r2,
                    'volume_r3': purchase.volume_r3,
                    'no_of_test': purchase.no_of_test
                }
                return make_response(jsonify({
                    'status': 'success',
                    'data': purchase_data
                })), 200
            else:
                # Get all purchases
                purchases = Purchase.query.all()
                purchases_data = []
                for purchase in purchases:
                    purchase_data = {
                        'id': purchase.id,
                        'unique_test': purchase.unique_test,
                        'company_na': purchase.company_na,
                        'price': purchase.price,
                        'volume_r1': purchase.volume_r1,
                        'volume_r2': purchase.volume_r2,
                        'volume_r3': purchase.volume_r3,
                        'no_of_test': purchase.no_of_test
                    }
                    purchases_data.append(purchase_data)
                return make_response(jsonify({
                    'status': 'success',
                    'data': purchases_data
                })), 200
        except Exception as e:
            return make_response(jsonify({
                'status': 'fail',
                'message': f'Error: {str(e)}'
            })), 500

    def post(self):
        """
        Create: Add a new purchase
        """
        try:
            # Get the post data
            post_data = request.get_json()
            if not post_data:
                return make_response(jsonify({
                    'status': 'fail',
                    'message': 'No data provided.'
                })), 400

            # Create a new purchase instance
            purchase = Purchase(
                unique_test=post_data.get('unique_test'),
                company_na=post_data.get('company_na'),
                price=post_data.get('price'),
                volume_r1=post_data.get('volume_r1'),
                volume_r2=post_data.get('volume_r2'),
                volume_r3=post_data.get('volume_r3'),
                no_of_test=post_data.get('no_of_test')
            )

            # Add the purchase to the database
            db.session.add(purchase)
            db.session.commit()

            return make_response(jsonify({
                'status': 'success',
                'message': 'Purchase created successfully.',
                'purchase_id': purchase.id
            })), 201
        except Exception as e:
            db.session.rollback()
            return make_response(jsonify({
                'status': 'fail',
                'message': f'Failed to create purchase: {str(e)}'
            })), 500

    def put(self, purchase_id):
        """
        Update: Update an existing purchase
        """
        try:
            # Find the purchase
            purchase = Purchase.query.get(purchase_id)
            if not purchase:
                return make_response(jsonify({
                    'status': 'fail',
                    'message': 'Purchase not found.'
                })), 404

            # Get the update data
            post_data = request.get_json()
            if not post_data:
                return make_response(jsonify({
                    'status': 'fail',
                    'message': 'No data provided.'
                })), 400

            # Update purchase fields
            purchase.unique_test = post_data.get('unique_test', purchase.unique_test)
            purchase.company_na = post_data.get('company_na', purchase.company_na)
            purchase.price = post_data.get('price', purchase.price)
            purchase.volume_r1 = post_data.get('volume_r1', purchase.volume_r1)
            purchase.volume_r2 = post_data.get('volume_r2', purchase.volume_r2)
            purchase.volume_r3 = post_data.get('volume_r3', purchase.volume_r3)
            purchase.no_of_test = post_data.get('no_of_test', purchase.no_of_test)

            db.session.commit()

            return make_response(jsonify({
                'status': 'success',
                'message': 'Purchase updated successfully.'
            })), 200
        except Exception as e:
            db.session.rollback()
            return make_response(jsonify({
                'status': 'fail',
                'message': f'Failed to update purchase: {str(e)}'
            })), 500

    def delete(self, purchase_id):
        """
        Delete: Delete a purchase
        """
        try:
            # Find the purchase
            purchase = Purchase.query.get(purchase_id)
            if not purchase:
                return make_response(jsonify({
                    'status': 'fail',
                    'message': 'Purchase not found.'
                })), 404

            # Delete the purchase
            db.session.delete(purchase)
            db.session.commit()

            return make_response(jsonify({
                'status': 'success',
                'message': 'Purchase deleted successfully.'
            })), 200
        except Exception as e:
            db.session.rollback()
            return make_response(jsonify({
                'status': 'fail',
                'message': f'Failed to delete purchase: {str(e)}'
            })), 500

# Register the API endpoints
purchase_view = PurchaseAPI.as_view('purchase_api')

# Define the API resources
purchase_blueprint.add_url_rule(
    '/purchase',
    view_func=purchase_view,
    methods=['GET', 'POST']  # GET (all purchases), POST (create)
)

purchase_blueprint.add_url_rule(
    '/purchase/<int:purchase_id>',
    view_func=purchase_view,
    methods=['GET', 'PUT', 'DELETE']  # GET (single purchase), PUT (update), DELETE (delete)
)


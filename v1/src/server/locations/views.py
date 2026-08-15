import datetime
import traceback

from flask import request
from flask_restx import Resource, fields, Namespace
from sqlalchemy import func

from src.server import db
from src.server.models import CardMember, Card, Location, Branch
from src.server.role_permission.utilty import authorize

# Swagger Namespace
locations_ns = Namespace('locations', description='Live GPS location operations')

# A fix older than this is flagged stale rather than treated as "live"
STALE_AFTER_SECONDS = 300

location_input_model = locations_ns.model('LocationInput', {
    'card_id': fields.Integer(description='Card ID (either card_id or imei_number is required)'),
    'imei_number': fields.String(description='Device IMEI number (alternative to card_id)'),
    'lat': fields.Float(required=True, description='Latitude'),
    'lng': fields.Float(required=True, description='Longitude'),
    'speed': fields.Float(description='Speed'),
    'battery': fields.Integer(description='Battery percentage remaining'),
    'sos_button_pressed': fields.Integer(description='SOS pressed (0=no, 1=yes)', default=0),
})

live_location_response_model = locations_ns.model('LiveLocationResponse', {
    'member_id': fields.Integer(description='Card Member ID'),
    'member_name': fields.String(description='Card member name'),
    'mobile': fields.String(description='Mobile number'),
    'branch_id': fields.Integer(description='Branch ID'),
    'branch_name': fields.String(description='Branch name'),
    'card_id': fields.Integer(description='Card ID'),
    'card_name': fields.String(description='Card name'),
    'imei_number': fields.String(description='Device IMEI number'),
    'lat': fields.Float(description='Latitude'),
    'lng': fields.Float(description='Longitude'),
    'speed': fields.Float(description='Speed'),
    'battery': fields.Integer(description='Battery percentage'),
    'timestamp': fields.String(description='Timestamp of the fix'),
    'sos_button_pressed': fields.Integer(description='SOS pressed (0/1)'),
    'is_stale': fields.Boolean(description='True if the latest fix is older than 5 minutes'),
    'has_fix': fields.Boolean(description='False if the card has never reported a location'),
})


def serialize_live_location(member, card, branch, location):
    """Serialize a card member + their card's latest location (if any) into one row."""
    has_fix = location is not None
    is_stale = False
    if has_fix and location.timestamp:
        age_seconds = (datetime.datetime.utcnow() - location.timestamp).total_seconds()
        is_stale = age_seconds > STALE_AFTER_SECONDS

    return {
        'member_id': member.id,
        'member_name': member.name,
        'mobile': member.mobile,
        'branch_id': member.branch_id,
        'branch_name': branch.name if branch else None,
        'card_id': card.id if card else None,
        'card_name': card.name if card else None,
        'imei_number': card.imei_number if card else None,
        'lat': float(location.lat) if has_fix else None,
        'lng': float(location.lng) if has_fix else None,
        'speed': float(location.speed) if has_fix and location.speed is not None else None,
        'battery': location.battery if has_fix else None,
        'timestamp': location.timestamp.isoformat() if has_fix and location.timestamp else None,
        'sos_button_pressed': location.sos_button_pressed if has_fix else 0,
        'is_stale': is_stale,
        'has_fix': has_fix,
    }


@locations_ns.route('/live')
class LiveLocationsAPI(Resource):
    """Latest known location per tracked employee, scoped to a branch or a single member."""

    @locations_ns.param('branch_id', 'Filter to employees in this branch')
    @locations_ns.param('member_id', 'Filter to a single card member')
    @locations_ns.response(200, 'Success', [live_location_response_model])
    @locations_ns.response(500, 'Internal server error')
    @locations_ns.doc(security='Bearer Auth')
    @authorize('locations.view')
    def get(self):
        """Get the latest location for each tracked card member (optionally filtered)"""
        try:
            branch_id = request.args.get('branch_id')
            member_id = request.args.get('member_id')

            # Only members who actually own a card can be tracked.
            query = CardMember.query.filter(CardMember.card_id.isnot(None))

            if member_id:
                query = query.filter(CardMember.id == member_id)
            elif branch_id:
                query = query.filter(CardMember.branch_id == branch_id)

            members = query.all()

            if not members:
                return {
                    'status': 'success',
                    'message': 'No tracked card members found.',
                    'data': [],
                    'total': 0
                }, 200

            card_ids = [m.card_id for m in members]

            # Latest location per card_id. Group on MAX(id) rather than MAX(timestamp)
            # so two fixes landing in the same second still resolve to exactly one row.
            latest_ids_subq = (
                db.session.query(
                    Location.card_id.label('card_id'),
                    func.max(Location.id).label('latest_id')
                )
                .filter(Location.card_id.in_(card_ids))
                .group_by(Location.card_id)
                .subquery()
            )

            latest_locations = (
                db.session.query(Location)
                .join(latest_ids_subq, Location.id == latest_ids_subq.c.latest_id)
                .all()
            )
            location_by_card = {loc.card_id: loc for loc in latest_locations}

            card_by_id = {c.id: c for c in Card.query.filter(Card.id.in_(card_ids)).all()}
            branch_ids = {m.branch_id for m in members}
            branch_by_id = {b.id: b for b in Branch.query.filter(Branch.id.in_(branch_ids)).all()}

            result = [
                serialize_live_location(
                    member,
                    card_by_id.get(member.card_id),
                    branch_by_id.get(member.branch_id),
                    location_by_card.get(member.card_id)
                )
                for member in members
            ]

            return {
                'status': 'success',
                'message': 'Live locations retrieved successfully.',
                'data': result,
                'total': len(result)
            }, 200

        except Exception as e:
            print(f"Error retrieving live locations: {traceback.format_exc()}")
            return {
                'status': 'fail',
                'message': f'Error retrieving live locations: {str(e)}'
            }, 500


@locations_ns.route('')
class LocationsAPI(Resource):
    """Ingestion endpoint: devices post new GPS fixes here."""

    @locations_ns.expect(location_input_model)
    @locations_ns.response(201, 'Location recorded successfully')
    @locations_ns.response(400, 'Invalid input')
    @locations_ns.response(404, 'Card not found')
    @locations_ns.response(500, 'Internal server error')
    @locations_ns.doc(security='Bearer Auth')
    @authorize('locations.create')
    def post(self):
        """Record a new GPS location fix for a card"""
        try:
            data = request.get_json()

            if not data:
                return {'status': 'fail', 'message': 'No JSON data provided'}, 400

            if data.get('lat') is None or data.get('lng') is None:
                return {
                    'status': 'fail',
                    'message': 'Missing required fields: lat and lng are required'
                }, 400

            card = None
            if data.get('card_id'):
                card = Card.query.get(data['card_id'])
            elif data.get('imei_number'):
                card = Card.query.filter_by(imei_number=data['imei_number']).first()

            if not card:
                return {
                    'status': 'fail',
                    'message': 'card_id or imei_number must reference an existing card'
                }, 404

            location = Location(
                card_id=card.id,
                lat=data['lat'],
                lng=data['lng'],
                speed=data.get('speed', 0),
                battery=data.get('battery'),
                sos_button_pressed=data.get('sos_button_pressed', 0),
            )

            db.session.add(location)
            db.session.commit()

            return {
                'status': 'success',
                'message': 'Location recorded successfully',
                'data': {'id': location.id, 'card_id': card.id}
            }, 201

        except Exception as e:
            db.session.rollback()
            print(f"Error recording location: {traceback.format_exc()}")
            return {
                'status': 'fail',
                'message': f'Error recording location: {str(e)}'
            }, 500
        finally:
            db.session.close()

from flask import Blueprint, jsonify

records_bp = Blueprint('records', __name__)

@records_bp.route('/records', methods=['GET'])
def get_records():
    return jsonify([])

from flask import Blueprint, jsonify

audit_bp = Blueprint('audit', __name__)

@audit_bp.route('/audit/runs', methods=['GET'])
def get_audit_runs():
    return jsonify([])

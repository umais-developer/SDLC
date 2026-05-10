from flask import Blueprint, jsonify

progress_bp = Blueprint('progress', __name__)

@progress_bp.route('/run/<run_id>/progress', methods=['GET'])
def get_progress(run_id):
    return jsonify({
        "processed": 0,
        "total": 0,
        "eta": "unknown"
    })

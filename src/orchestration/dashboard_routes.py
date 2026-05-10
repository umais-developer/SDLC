from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/runs', methods=['GET'])
def get_runs():
    return jsonify([])

@app.route('/runs/<run_id>/retry', methods=['POST'])
def retry_run(run_id):
    return jsonify({"status": "retry_initiated"})

"""Serveur Web de Production - Flask"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from config import config
from api.routes import api_routes

app = Flask(__name__)
CORS(app)

# Routes
@app.route('/health', methods=['GET'])
def health():
    res, status = api_routes.health_check()
    return jsonify(res), status

@app.route('/stats', methods=['GET'])
def stats():
    res, status = api_routes.get_stats()
    return jsonify(res), status

@app.route('/prospects', methods=['POST'])
def create_prospect():
    data = request.get_json() or {}
    res, status = api_routes.create_prospect(data)
    return jsonify(res), status

@app.route('/prospects/<int:prospect_id>', methods=['GET'])
def get_prospect(prospect_id):
    res, status = api_routes.get_prospect(prospect_id)
    return jsonify(res), status

@app.route('/prospects', methods=['GET'])
def list_prospects():
    limit = request.args.get('limit', 50, type=int)
    res, status = api_routes.list_prospects(limit=limit)
    return jsonify(res), status

@app.route('/messages/generate', methods=['POST'])
def generate_message():
    data = request.get_json() or {}
    prospect_id = data.get('prospect_id')
    pain_points = data.get('pain_points', [])
    res, status = api_routes.generate_message(prospect_id, pain_points)
    return jsonify(res), status

# Security headers
@app.after_request
def apply_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=config.DEBUG)

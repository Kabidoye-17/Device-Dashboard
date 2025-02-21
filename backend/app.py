from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS
from utils.logger import get_logger, setup_logger
import traceback
from aggregator import DatabaseAggregator
from config.config import load_config

# Initialize application with config
app = Flask(__name__)
CORS(app)

# Load and apply configuration
config = load_config()
app.config.from_object(config)

# Setup logging after config is loaded
logger = setup_logger(config)
logger.info("Logger initialized with configuration")

# Initialize aggregator
try:
    db_aggregator = DatabaseAggregator(config.SQLALCHEMY_DATABASE_URI)
    logger.info("Database aggregator initialized successfully")
except Exception as e:
    logger.critical(f"Failed to initialize database aggregator: {str(e)}")
    raise

# Keep only these two essential routes
@app.route('/api/metrics/metrics', methods=['POST'])
def receive_metrics():
    try:
        metrics_data = request.json
        if not metrics_data:
            return jsonify({'error': 'No metrics data received'}), 400

        db_aggregator.store_metrics(metrics_data)
        return jsonify({'status': 'success', 'count': len(metrics_data)}), 200

    except Exception as e:
        logger.error(f"Error processing metrics: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/metrics', methods=['GET'])
def get_metrics():
    try:
        metrics = db_aggregator.get_latest_metrics()
        return jsonify(metrics), 200
    except Exception as e:
        logger.error(f"Error fetching metrics: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.errorhandler(500)
def handle_500_error(e):
    logger.error(f"Internal server error: {str(e)}")
    return jsonify({
        "error": "Internal server error",
        "message": str(e)
    }), 500

@app.errorhandler(404)
def handle_404_error(e):
    logger.warning(f"Route not found: {request.url}")
    return jsonify({
        "error": "Not found",
        "message": f"Route {request.url} not found"
    }), 404

if __name__ == '__main__':
    logger.info("Starting Flask application...")
    app.run(debug=True, host='0.0.0.0', port=5000)
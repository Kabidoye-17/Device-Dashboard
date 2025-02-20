from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS
from utils.logger import get_logger, setup_logger
from metric_queue.queue_manager import MetricsStore  # Changed from UploaderQueue to MetricsStore
import traceback
from services.db_service import DatabaseService
from config import Config, load_config

app = Flask(__name__)
# Update CORS to explicitly allow all methods
CORS(app, resources={
    r"/api/*": {"origins": "*", "methods": ["GET", "POST"]},
    r"/*": {"origins": "*", "methods": ["GET"]}
})

# Load config first
config = load_config()
# Setup logger with config
logger = setup_logger(config)

# Single metrics store instance
metrics_store = MetricsStore()  # This doesn't need server_url parameter
logger.info("Initialized metrics store")

try:
    # Initialize database service with config
    db_service = DatabaseService(config.SQLALCHEMY_DATABASE_URI)
    logger.info("Application initialized successfully")
except Exception as e:
    logger.critical(f"Failed to initialize application: {str(e)}")
    raise

@app.route('/metrics', methods=['GET'])
def get_all_metrics():
    logger.info('All metrics endpoint accessed')
    try:
        latest_metrics = db_service.get_latest_metrics()
        metrics_data = [{
            'id': metric.id,
            'name': metric.name,
            'value': metric.value,
            'type': metric.type.name,
            'unit': metric.unit.unit_name,
            'source': metric.source.name,
            'timestamp': metric.timestamp.isoformat()
        } for metric in latest_metrics]
        return jsonify(metrics_data)
    except Exception as e:
        logger.error(f'Error in all metrics: {str(e)}')
        logger.error(f'Traceback: {traceback.format_exc()}')
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/api/metrics/system', methods=['POST'])
def receive_system_metrics():
    """Endpoint to receive system metrics from local collector"""
    try:
        metrics = request.get_json()
        logger.debug(f"Received system metrics payload: {metrics}")
        if not metrics:
            raise ValueError("Empty metrics payload")
        
        # Transform metrics to include type and source
        for metric in metrics:
            metric['type'] = 'system'
            metric['source'] = 'system_collector'
            
        db_service.store_metrics(metrics)
        logger.info("Successfully stored system metrics")
        return jsonify({"status": "success"}), 200
        
    except Exception as e:
        logger.error(f"Error processing system metrics: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500

@app.route('/api/metrics/crypto', methods=['POST'])
def receive_crypto_metrics():
    """Endpoint to receive crypto metrics from local collector"""
    try:
        metrics = request.get_json()
        # Transform metrics to include type and source
        for metric in metrics:
            metric['type'] = 'crypto'
            metric['source'] = 'crypto_collector'
            
        db_service.store_metrics(metrics)
        logger.info("Successfully stored crypto metrics")
        return jsonify({"status": "success"}), 200
    except Exception as e:
        logger.error(f"Error receiving crypto metrics: {str(e)}")
        return jsonify({"error": str(e)}), 500

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
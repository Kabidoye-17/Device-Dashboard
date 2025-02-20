from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS
from utils.logger import get_logger, setup_logger
from metric_queue.queue_manager import MetricsStore  # Changed from UploaderQueue to MetricsStore
import traceback
from services.db_service import DatabaseService
from config import Config, load_config

# Initialize application with config
app = Flask(__name__)
CORS(app, resources={
    r"/api/*": {"origins": "*", "methods": ["GET", "POST"]},
    r"/*": {"origins": "*", "methods": ["GET"]}
})

# Load and apply configuration
config = load_config()
app.config.from_object(config)

# Setup logging after config is loaded
logger = setup_logger(config)
logger.info("Logger initialized with configuration")

# Initialize services
try:
    metrics_store = MetricsStore()
    db_service = DatabaseService(config.SQLALCHEMY_DATABASE_URI)
    logger.info("Application services initialized successfully")
except Exception as e:
    logger.critical(f"Failed to initialize application services: {str(e)}")
    raise

@app.route('/metrics', methods=['GET'])
def get_all_metrics():
    logger.info('All metrics endpoint accessed')
    try:
        # Add connection verification
        if not db_service.verify_connection():
            logger.error("Database connection failed")
            return jsonify({
                'error': 'Database connection failed',
                'note': 'This might be due to PythonAnywhere free tier restrictions'
            }), 500
            
        metrics_data = db_service.get_latest_metrics()
        logger.info(f"Retrieved {len(metrics_data) if metrics_data else 0} metrics")
        return jsonify(metrics_data or [])
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
        if not metrics:
            return jsonify({"error": "Empty metrics payload"}), 400
            
        logger.debug(f"Received crypto metrics: {metrics}")
        
        # More lenient validation
        for metric in metrics:
            required_fields = {'name', 'value'}
            missing_fields = required_fields - set(metric.keys())
            if missing_fields:
                logger.error(f"Missing required fields: {missing_fields}")
                return jsonify({"error": f"Missing required fields: {missing_fields}"}), 400

            # Ensure value is numeric
            try:
                metric['value'] = float(metric['value'])
            except (TypeError, ValueError):
                logger.error(f"Invalid value format for metric: {metric}")
                return jsonify({"error": f"Invalid value format for metric: {metric}"}), 400

            # Add required fields if missing
            metric['timestamp'] = metric.get('timestamp', datetime.utcnow().timestamp())
            metric['type'] = 'crypto'
            metric['source'] = 'crypto_collector'
            metric['unit'] = metric.get('unit', 'unknown')
            
        db_service.store_metrics(metrics)
        logger.info("Successfully stored crypto metrics")
        return jsonify({"status": "success"}), 200
    except Exception as e:
        logger.error(f"Error receiving crypto metrics: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
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
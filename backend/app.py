from flask import Flask, jsonify, request
from flask_cors import CORS
from utils.logger import get_logger, setup_logger
import traceback
from aggregator import DatabaseAggregator
from config.config import load_config
from reporting import MetricsReporter

# Initialize application with config
app = Flask(__name__)
CORS(app)

# Load and apply configuration
config = load_config()
app.config.from_object(config)

# Setup logging after config is loaded
logger = setup_logger(config)
logger.info("Logger initialized with configuration")

# Add debug logging right after app initialization
logger.info("Initializing Flask routes...")

# Initialize aggregator
try:
    db_aggregator = DatabaseAggregator(config.SQLALCHEMY_DATABASE_URI)
    logger.info("Database aggregator initialized successfully")
except Exception as e:
    logger.critical(f"Failed to initialize database aggregator: {str(e)}")
    raise

try:
    metrics_reporter = MetricsReporter(config.SQLALCHEMY_DATABASE_URI)
    logger.info("Metrics reporter initialized successfully")
except Exception as e:
    logger.critical(f"Failed to initialize Metrics reporter: {str(e)}")
    raise

@app.route('/api/metrics/upload-metrics', methods=['POST'])
def handle_metrics():
    logger.debug(f"Handling {request.method} request to /api/metrics")
    try:
            metrics_data = request.json
            if not metrics_data:
                return jsonify({'error': 'No metrics data received'}), 400
            
            logger.info(f"metrics_data in upload enpoint  ☀️: {metrics_data}")
            db_aggregator.store_metrics(metrics_data)
            return jsonify({'status': 'success', 'count': len(metrics_data)}), 200
    except Exception as e:
        logger.error(f"Error in handle_metrics: {str(e)}")


@app.route('/api/metrics/get-latest-metrics', methods=['GET'])
def get_latest_batch():
    logger.debug("Handling GET request to get-latest-metrics")
    try:
        metrics = metrics_reporter.get_latest_metrics(50)
        logger.info(f"metrics_data in get enpoint  ☀️☀️☀️: {metrics}")
        logger.info(f"Storing {len(metrics)} metrics")
        
        # Verify data before sending
        if not metrics:
            return jsonify([]), 200
        
        return jsonify(metrics), 200
    except Exception as e:
        logger.error(f"Error in get_latest_batch: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

# Add a test route to verify the application is running
@app.route('/', methods=['GET'])
def health_check():
    return jsonify({
        "status": "ok",
        "message": "API is running",
        "routes": [str(rule) for rule in app.url_map.iter_rules()]
    })

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

# Log all registered routes after they're defined
logger.info("Registered routes:")
def log_routes():
    for rule in app.url_map.iter_rules():
        logger.info(f"Route: {rule.rule} Methods: {rule.methods}")

# Call route logging after all routes are registered
log_routes()

if __name__ == '__main__':
    logger.info("Starting Flask application...")
    app.run(debug=True, host='0.0.0.0', port=5000)
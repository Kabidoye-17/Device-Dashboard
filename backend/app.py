from flask import Flask, jsonify, request
from flask_cors import CORS
from utils.logger import get_logger, setup_logger
import traceback
from aggregator import DatabaseAggregator
from config.config import load_config
from reporting import MetricsReporter
from cache import CachedData, CacheUpdateManager

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

# Initialize cache for metrics
metrics_cache = CachedData(cache_duration_seconds=10)  # Changed from 30 to 10 seconds
current_site = None

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
        metric_type = request.args.get('metric_type')
        logger.debug(f"Received metric_type: {metric_type}")

        with metrics_cache:
            if not metrics_cache.is_expired():
                logger.info("Serving metrics from cache")
                return jsonify(metrics_cache.get_data()), 200

            with CacheUpdateManager(metrics_cache) as manager:
                if manager.update_started_elsewhere():
                    logger.info("Waiting for another thread to update the cache")
                    manager.spin_wait_for_update_to_complete()
                    return jsonify(metrics_cache.get_data()), 200

                logger.info("Fetching new metrics data")
                metrics = metrics_reporter.get_latest_metrics(metric_type)
                if not metrics:
                    return jsonify([]), 200

                metrics_cache.update(metrics)
                logger.info("Cache updated with new metrics data")
                return jsonify(metrics), 200
    except Exception as e:
        logger.error(f"Error in get_latest_batch: {str(e)}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500

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

# Add this new endpoint
@app.route('/api/poll-site', methods=['GET'])
def poll_site():
    global current_site  # We modify this global variable
    logger.debug("Received poll request for site opening")

    try:
        if current_site is not None:
            site_to_return = current_site  # Store the site URL temporarily
            current_site = None  # Reset after serving it once
            return jsonify({"status": "success", "site": site_to_return}), 200

        return jsonify({"status": "no_data"}), 200

    except Exception as e:
        logger.error(f"Error in poll_site: {str(e)}")
        return jsonify({"error": str(e)}), 500
@app.route('/api/recieve-site', methods=['POST'])
def receive_site():
    global current_site  # Indicate that we are modifying the global variable
    try:
        data = request.get_json()
        current_site = data.get('site_url')  # Update the global variable

        if not current_site:
            logger.error("No trading site received")
            return jsonify({"error": "No site URL provided"}), 400

        logger.info(f"{current_site} retrieved")
        
        return jsonify({
            "status": "success",
            "message": "Site sent for opening"
        }), 200

    except Exception as e:
        logger.error(f"Error in receive_site: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    logger.info("Starting Flask application...")
    app.run(debug=True, host='0.0.0.0', port=5000)
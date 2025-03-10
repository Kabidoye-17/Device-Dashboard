import dataclasses
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

collector_types = config.collector_types
collector_type_values = {field.name: getattr(collector_types, field.name) for field in dataclasses.fields(collector_types)}
metrics_cache = {metric_type: CachedData(cache_duration_seconds=30) for metric_type in collector_type_values.values()}
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
    """
    Get latest metrics with pagination and caching support.
    Query parameters:
    - metric_type: Type of metrics to retrieve
    - page_number: Page number for pagination (default: 1)
    """
    logger.debug("Handling GET request to get-latest-metrics")
    try:
        # Validate and extract parameters
        metric_type, page_number = _validate_metrics_request_params()
        if not metric_type:
            return jsonify({'error': 'Invalid metric type'}), 400

        page_size = 10  # Fixed page size for pagination
        logger.debug(f"Processing request for metric_type: {metric_type}, page_number: {page_number}")

        # Get metrics data (from cache or database)
        metrics_data = _get_metrics_data(metric_type)
        if not metrics_data:
            return _create_empty_response(), 200

        # Process the metrics data
        latest_metrics = _extract_latest_metrics(metrics_data)
        page_data, pagination_info = _paginate_metrics(metrics_data, page_number, page_size)

        logger.info(f"Serving page {pagination_info['current_page']} of {pagination_info['total_pages']} for {metric_type} metrics")
        return jsonify({
            'latest_metric': latest_metrics,
            'metrics': page_data,
            'total_pages': pagination_info['total_pages'],
            'current_page': pagination_info['current_page']
        }), 200

    except Exception as e:
        logger.error(f"Error in get_latest_batch: {str(e)}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500


def _validate_metrics_request_params():
    """
    Validate and extract request parameters.
    Returns tuple: (metric_type, page_number)
    """
    metric_type = request.args.get('metric_type')
    if metric_type not in metrics_cache:
        return None, None

    try:
        page_number = max(1, int(request.args.get('page_number', 1)))
    except (ValueError, TypeError):
        page_number = 1

    return metric_type, page_number


def _get_metrics_data(metric_type):
    """
    Get metrics data from cache or database.
    Handles cache expiration and updates.
    Returns the metrics data or None if no data is available.
    """
    cache = metrics_cache[metric_type]

    with cache:
        if cache.is_expired():
            _update_cache_if_needed(cache, metric_type)
        else:
            logger.info(f"Serving {metric_type} metrics from cache")

        all_data = cache.get_data()

    # Return flattened metrics or None if no data
    return all_data[0] if all_data and all_data[0] else None


def _update_cache_if_needed(cache, metric_type):
    """
    Update the cache if needed and not already being updated by another thread.
    """
    with CacheUpdateManager(cache) as manager:
        if not manager.update_started_elsewhere():
            logger.info(f"Fetching new {metric_type} metrics data")
            new_data = metrics_reporter.get_all_latest_metrics(metric_type=metric_type)
            if new_data:
                cache.update(new_data)
                logger.info(f"Cache updated with {len(new_data)} {metric_type} metrics")
        else:
            logger.info(f"Waiting for another thread to update the {metric_type} cache")
            manager.spin_wait_for_update_to_complete()


def _extract_latest_metrics(metrics_data):
    """
    Extract the latest metrics for each device in a single pass.
    Returns a list of the latest metrics for each device.
    """
    device_timestamps = {}
    for metric in metrics_data:
        device_name = metric['device_name']
        timestamp = metric['timestamp_utc']
        if device_name not in device_timestamps or timestamp > device_timestamps[device_name]:
            device_timestamps[device_name] = timestamp

    return [
        metric for metric in metrics_data
        if metric['timestamp_utc'] == device_timestamps[metric['device_name']]
    ]


def _paginate_metrics(metrics_data, page_number, page_size):
    """
    Paginate the metrics data.
    Returns tuple: (page_data, pagination_info)
    """
    total_count = len(metrics_data)
    total_pages = (total_count + page_size - 1) // page_size if total_count > 0 else 0
    page_number = min(page_number, total_pages) if total_pages > 0 else 1

    start_idx = (page_number - 1) * page_size
    page_data = metrics_data[start_idx:start_idx + page_size] if start_idx < total_count else []

    return page_data, {
        'total_pages': total_pages,
        'current_page': page_number
    }


def _create_empty_response():
    """
    Create an empty response when no metrics data is available.
    """
    return jsonify({
        'latest_metric': [],
        'metrics': [],
        'total_pages': 0,
        'current_page': 1
    })

# Add a test route to verify the application is running
@app.route('/', methods=['GET'])
def health_check():
    return jsonify({
        "status": "ok",
        "message": "API is running",
        "routes": [str(rule) for rule in app.url_map.iter_rules()]
    })

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
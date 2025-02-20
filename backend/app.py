from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS
from utils.logger import get_logger
from metric_queue.queue_manager import MetricsStore  # Changed from UploaderQueue to MetricsStore
import traceback

app = Flask(__name__)
# Update CORS to explicitly allow all methods
CORS(app, resources={
    r"/api/*": {"origins": "*", "methods": ["GET", "POST"]},
    r"/*": {"origins": "*", "methods": ["GET"]}
})
logger = get_logger()

# Single metrics store instance
metrics_store = MetricsStore()  # This doesn't need server_url parameter
logger.info("Initialized metrics store")

@app.route('/metrics', methods=['GET'])
def get_all_metrics():
    logger.info('All metrics endpoint accessed')
    try:
        latest_data = metrics_store.get_latest_metrics()
        logger.debug(f"Raw metrics data: {latest_data}")

        system_data = latest_data['system_metrics']
        crypto_data = latest_data['crypto_metrics']

        all_metrics = system_data + [item for sublist in crypto_data.values() for item in sublist]
        return jsonify(all_metrics)
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
            
        metrics_store.update_system_metrics(metrics)
        logger.info("Successfully updated system metrics")
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
        metrics_store.update_crypto_metrics(metrics)
        logger.info("Received crypto metrics update")
        return jsonify({"status": "success"}), 200
    except Exception as e:
        logger.error(f"Error receiving crypto metrics: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
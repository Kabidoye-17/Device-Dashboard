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

@app.route('/system-metrics', methods=["GET"])  # Explicitly allow GET
def get_system_metrics():
    logger.info('System metrics endpoint accessed')
    try:
        latest_data = metrics_store.get_latest_metrics()
        logger.debug(f"Raw metrics data: {latest_data}")
        
        metrics = latest_data['system_metrics']
        if not metrics:
            logger.warning("No system metrics found in store")
            return jsonify({
                'cpu_load': 0,
                'ram_usage': 0,
                'network_sent': 0,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'status': 'no_data'
            })
        
        # Transform list of measurements into expected format
        formatted_metrics = {
            'cpu_load': next((m['value'] for m in metrics if m['name'] == 'cpu_load'), 0),
            'ram_usage': next((m['value'] for m in metrics if m['name'] == 'ram_usage'), 0),
            'network_sent': next((m['value'] for m in metrics if m['name'] == 'network_sent'), 0),
            'timestamp': next((m['timestamp'] for m in metrics), datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        }
        return jsonify(formatted_metrics)
    except Exception as e:
        logger.error(f'Error in system metrics: {str(e)}')
        logger.error(f'Traceback: {traceback.format_exc()}')
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

# Update valid pairs list
VALID_PAIRS = ['BTC-USD', 'ETH-USD'] 
@app.route('/crypto-ticker/<currency_pair>', methods=["GET"])  # Explicitly allow GET
def get_crypto_ticker(currency_pair):
    logger.info('Crypto metrics endpoint accessed')
    try:
        latest_data = metrics_store.get_latest_metrics()
        crypto_data = latest_data['crypto_metrics'].get(currency_pair, [])
        
        if crypto_data:
            # Transform list of measurements into expected format
            formatted_crypto = {
                'price': next((m['value'] for m in crypto_data if m['name'] == f'{currency_pair}_price'), 0),
                'bid': next((m['value'] for m in crypto_data if m['name'] == f'{currency_pair}_bid'), 0),
                'ask': next((m['value'] for m in crypto_data if m['name'] == f'{currency_pair}_ask'), 0),
                'timestamp': next((m['timestamp'] for m in crypto_data), datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                'currency_pair': currency_pair
            }
            return jsonify(formatted_crypto)
        return jsonify({'error': 'No data available for this currency pair'}), 404
    except Exception as e:
        logger.error(f'Error fetching crypto data: {str(e)}')
        return jsonify({'error': str(e)}), 500

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
import time
from flask import Flask, jsonify, request
from flask_cors import CORS
from logger import get_logger
import git
from models import SystemMetrics, CryptoTicker
import requests

app = Flask(__name__) 
CORS(app)
logger = get_logger()

@app.route('/')
def home():
    logger.info('Home endpoint accessed')
    return {'message': 'Flask server is running!'}


@app.route('/system-metrics')
def get_system_metrics():
    logger.info('System metrics endpoint accessed')
    try:
        metrics = SystemMetrics.get_current_metrics()
        return jsonify({
            'cpu_load': metrics.cpu_load,
            'ram_usage': metrics.ram_usage,
            'network_sent': metrics.network_sent,
            'timestamp': metrics.timestamp
        })
    except Exception as e:
        logger.error(f'Error fetching system metrics: {str(e)}')
        logger.error('Full traceback:', exc_info=True)
        return jsonify({'error': str(e)}), 500

VALID_PAIRS = ['BTC-USD', 'ETH-USD', 'DOGE-USD']

@app.route('/crypto-ticker/<currency_pair>')
def get_crypto_ticker(currency_pair):
    logger.info('Crypto metrics endpoint accessed')
    
    if currency_pair not in VALID_PAIRS:
        logger.warning(f'Invalid currency pair attempted: {currency_pair}')
        return {'error': f'Invalid currency pair. Must be one of: {VALID_PAIRS}'}, 400
        
    try:
        response = requests.get(f'https://api.exchange.coinbase.com/products/{currency_pair}/ticker')
        response.raise_for_status()
        data = response.json()
        
        logger.info(f'Raw API response data type: {type(data)}')
        logger.info(f'Raw API response content: {data}')
        
        ticker = CryptoTicker.from_json(data)
        
        return {
            'price': ticker.price,
            'bid': ticker.bid,
            'ask': ticker.ask,
            'timestamp': ticker.timestamp,
            'currency_pair': currency_pair
        }

    except Exception as e:
        logger.error(f'Error fetching crypto data: {str(e)}')
        logger.error('Full traceback:', exc_info=True)
        return {'error': str(e)}, 500


@app.route('/update_server', methods=['POST'])
def webhook():
    if request.method == 'POST':
        try:
            repo = git.Repo('/home/Kabidoye17/Device-Dashboard')
            origin = repo.remotes.origin
            origin.pull()
            return 'Updated PythonAnywhere successfully', 200
        except Exception as e:
            logger.error(f'Git pull failed: {str(e)}')
            return str(e), 500
    return 'Wrong event type', 400

if __name__ == '__main__':
    logger.info('Starting Flask application')
    logger.info('testing')
    app.run(debug=True)
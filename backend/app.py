import time
from flask import Flask, jsonify, request
from flask_cors import CORS
from logger import get_logger
import git
import hmac
import os
import hashlib

app = Flask(__name__) 
CORS(app)
logger = get_logger()

@app.route('/')
def home():
    logger.info('Home endpoint accessed')
    return {'message': 'Flask server is running!'}

@app.route('/word')
def get_current_word():
    logger.info('Word endpoint accessed')
    try:
        return {'word': 'woof'}
    except Exception as e:
        logger.error(f'Error in get_current_word: {str(e)}')
        return jsonify({'error': str(e)}), 500

@app.route('/update_server', methods=['POST'])
def webhook():
    if request.method == 'POST':
        logger.info('Received webhook request')
        # Verify GitHub webhook signature
        signature = request.headers.get('X-Hub-Signature')
        if not signature or not signature.startswith('sha1='):
            logger.error('Invalid signature format')
            return 'Invalid signature', 400
            
        # Get the secret from environment variable
        secret = os.environ.get('WEBHOOK_SECRET')
        if not secret:
            logger.error('Webhook secret not configured')
            return 'Server configuration error', 500
            
        secret = secret.encode()
        
        # Create hmac signature from payload
        hmac_obj = hmac.new(secret, request.data, hashlib.sha1)
        expected_signature = 'sha1=' + hmac_obj.hexdigest()
        
        if not hmac.compare_digest(signature, expected_signature):
            logger.error('Invalid signature')
            return 'Invalid signature', 400

        try:
            repo = git.Repo('/home/Kabidoye17/Device-Dashboard')
            origin = repo.remotes.origin
            origin.pull()
            logger.info('Successfully pulled updates')
            return 'Updated PythonAnywhere successfully', 200
        except Exception as e:
            logger.error(f'Git pull failed: {str(e)}')
            return f'Git pull failed: {str(e)}', 500
    return 'Wrong event type', 400

if __name__ == '__main__':
    logger.info('Starting Flask application')
    app.run(debug=True)
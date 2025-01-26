import time
from flask import Flask, jsonify
from flask_cors import CORS
from logger import get_logger

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

if __name__ == '__main__':
    logger.info('Starting Flask application')
    app.run(debug=True)
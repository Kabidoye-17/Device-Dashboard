import time
from flask import Flask, jsonify, request
from flask_cors import CORS
from logger import get_logger
import git


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
import time
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__) 
CORS(app)

@app.route('/')
def home():
    return {'message': 'Flask server is running!'}

@app.route('/word')
def get_current_word():
        return {'word': 'woof'}

if __name__ == '__main__':
    app.run(debug=True)
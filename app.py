from flask import Flask, jsonify
from flask_cors import CORS
from customers import user_data


app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/')
def home():
    data = {'message': user_data}
    return jsonify(data)

@app.route('/status')
def status():
    status_info = {'status': 'running', 'uptime': '48 hours'}
    return jsonify(status_info)

if __name__ == '__main__':
    app.run(debug=True)

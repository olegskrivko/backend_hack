from flask import Flask, jsonify, request
from flask_cors import CORS
import yfinance as yf
from openai import OpenAI
from customers import user_data
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/')
def home():
    data = {'message': user_data}
    return jsonify(data)

# Ensure the app listens on the right port for deployment
if __name__ == '__main__':
    # Use the environment variable PORT, or fallback to 5000 in local development
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)), debug=True)

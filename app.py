from flask import Flask, jsonify, request
from flask_cors import CORS
import yfinance as yf
from openai import OpenAI
from customers import user_data
import os
from dotenv import load_dotenv 


#http://127.0.0.1:5000/stocks?symbol=AAPL

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/')
def home():
    data = {'message': user_data}
    return jsonify(data)



if __name__ == '__main__':
    app.run(debug=True)

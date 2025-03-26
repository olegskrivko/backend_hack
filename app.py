from flask import Flask, jsonify, request
from flask_cors import CORS
import yfinance as yf
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

@app.route('/stocks', methods=['GET'])
def stocks():
    print("Before stocks")
    # Get the stock symbol from the query parameter
    stock_symbol = request.args.get('symbol')

    # Check if stock symbol is provided
    if not stock_symbol:
        return jsonify({'error': 'Stock symbol is required'}), 400

    # Fetching Yahoo Finance data for the specified stock symbol
    try:
        stock = yf.Ticker(stock_symbol)
        data = stock.history(period="1y")  # Get 1 year of historical data
        stock_data = data.to_dict(orient='records')  # Convert data to a list of dictionaries
    except Exception as e:
        return jsonify({'error': f'Error fetching data for {stock_symbol}: {str(e)}'}), 500

    # Return the stock data as JSON
    return jsonify({'stock_data': stock_data})

if __name__ == '__main__':
    app.run(debug=True)

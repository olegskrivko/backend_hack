from flask import Flask, jsonify
from flask_cors import CORS

user_data = {
    "user": {
      "id": 1,
      "name": "Jane Doe",
      "email": "jane.doe@example.com",
      "phone": "+1234567890",
      "address": {
        "street": "123 Elm Street",
        "city": "Springfield",
        "state": "IL",
        "zip": "62701",
        "country": "USA"
      },
      "portfolio": {
        "stocks": [
          {
            "symbol": "AAPL",
            "company": "Apple Inc.",
            "quantity": 50,
            "purchase_price": 145.30,
            "current_price": 150.00,
            "purchase_date": "2023-05-15"
          },
          {
            "symbol": "GOOGL",
            "company": "Alphabet Inc.",
            "quantity": 10,
            "purchase_price": 2725.00,
            "current_price": 2800.00,
            "purchase_date": "2022-11-20"
          },
          {
            "symbol": "AMZN",
            "company": "Amazon.com Inc.",
            "quantity": 5,
            "purchase_price": 3450.50,
            "current_price": 3300.00,
            "purchase_date": "2021-08-10"
          }
        ],
        "total_investment": 0,
        "current_value": 0,
        "profit_loss": 0
      }
    }
  }
  

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

from flask import Flask, jsonify, request
from flask_cors import CORS
import yfinance as yf
from openai import OpenAI
from customers import user_data
import os
from dotenv import load_dotenv 

# Load environment variables from .env
load_dotenv()

# Set OpenAI API key from .env
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

#http://127.0.0.1:5000/stocks?symbol=AAPL

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/')
def home():
    data = {'message': user_data}
    return jsonify(data)

@app.route('/customer')
def status():
    status_info = {'status': 'running', 'uptime': '48 hours'}
    return jsonify(status_info)

@app.route('/stocks', methods=['GET'])
def stocks():
    stock_symbol = request.args.get('symbol')

    if not stock_symbol:
        return jsonify({'error': 'Stock symbol is required'}), 400

    try:
        stock = yf.Ticker(stock_symbol)
        data = stock.history(period="1mo")  # Get 1 month of historical data
        
        if data.empty:
            return jsonify({'error': 'No stock data found for this symbol'}), 404

        # Convert stock data to a list of dictionaries
        stock_data = data.reset_index()[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']].to_dict(orient='records')

        # Generate AI-based stock analysis
        ai_response = generate_ai_insight(stock_symbol, stock_data)

    except Exception as e:
        return jsonify({'error': f'Error fetching data for {stock_symbol}: {str(e)}'}), 500

    return jsonify({'stock_data': stock_data, 'ai_insight': ai_response})

def generate_ai_insight(symbol, stock_data):
    """Generate AI insights using OpenAI API based on 1-month stock data"""
    
    # Extract key statistics
    closing_prices = [day['Close'] for day in stock_data]
    highest_price = max(closing_prices)
    lowest_price = min(closing_prices)
    avg_price = sum(closing_prices) / len(closing_prices)
    
    summary = (
        f"Stock: {symbol}\n"
        f"Highest price in last month: ${highest_price:.2f}\n"
        f"Lowest price in last month: ${lowest_price:.2f}\n"
        f"Average closing price: ${avg_price:.2f}\n"
    )

    prompt = f"{summary}\nBased on this data, analyze how the stock has been performing over the past month and provide an investment insight."

    try:
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a financial analyst providing stock insights."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    
    except Exception as e:
        return f"AI analysis unavailable: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True)

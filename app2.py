from flask import Flask, jsonify
from flask_cors import CORS
import os
from openai import OpenAI
from dotenv import load_dotenv
from customers import user_data 

# Load environment variables from .env
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/')
def home():
    return jsonify({'message': 'Welcome to the Investment Analysis API'})


@app.route('/portfolio', methods=['GET'])
def portfolio_analysis():
    """Analyzes the user's stock portfolio using AI"""
    
    user = user_data.get("user", {})
    portfolio = user.get("portfolio", {})
    stocks = portfolio.get("stocks", [])

    if not stocks:
        return jsonify({"error": "No stocks found in portfolio"}), 404

    # Calculate total investment, current value, and profit/loss
    total_investment = sum(stock["purchase_price"] * stock["quantity"] for stock in stocks)
    current_value = sum(stock["current_price"] * stock["quantity"] for stock in stocks)
    profit_loss = current_value - total_investment

    # Update portfolio data
    portfolio["total_investment"] = total_investment
    portfolio["current_value"] = current_value
    portfolio["profit_loss"] = profit_loss

    # Generate AI-based investment insight
    ai_insight = analyze_portfolio(user["name"], stocks, total_investment, current_value, profit_loss)

    return jsonify({"ai_insight": ai_insight})
    #return jsonify({"portfolio": portfolio, "ai_insight": ai_insight})

def analyze_portfolio(name, stocks, total_investment, current_value, profit_loss):
    """Generates AI insights for the user's investment portfolio"""

    # Create a summary of the portfolio
    stock_summary = "\n".join(
        f"- {stock['symbol']} ({stock['company']}): {stock['quantity']} shares | Purchased at ${stock['purchase_price']} | Current price ${stock['current_price']}"
        for stock in stocks
    )

    summary = (
        f"Investor: {name}\n"
        f"Total Investment: ${total_investment:.2f}\n"
        f"Current Portfolio Value: ${current_value:.2f}\n"
        f"Overall Profit/Loss: ${profit_loss:.2f}\n"
        f"Stock Holdings:\n{stock_summary}\n"
    )

    prompt = f"{summary}\nBased on this data, analyze the investor's performance and provide suggestions for improving their portfolio."

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a financial analyst providing investment portfolio insights."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content

    except Exception as e:
        return f"AI analysis unavailable: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True)

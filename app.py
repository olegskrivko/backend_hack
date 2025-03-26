from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import yfinance as yf
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

# http://127.0.0.1:5000/portfolio/assets

@app.route('/portfolio/assets', methods=['GET'])
def analyze_assets():
    """Analyzes asset allocation in the user's portfolio"""
    portfolio = user_data["user"]["portfolio"]

    asset_allocation = {
        "Stocks": sum(stock["current_price"] * stock["quantity"] for stock in portfolio.get("stocks", [])),
        "Funds": sum(fund["current_price"] * fund["quantity"] for fund in portfolio.get("funds", [])),
        "Bonds": sum(bond["current_price"] * bond["quantity"] for bond in portfolio.get("bonds", [])),
        "Cash": portfolio.get("cash", {}).get("amount", 0)
    }

    total_value = sum(asset_allocation.values())
    allocation_percent = {k: (v / total_value) * 100 if total_value else 0 for k, v in asset_allocation.items()}

    ai_insight = generate_ai_insight("asset allocation", asset_allocation, allocation_percent)

    return jsonify({"asset_allocation": allocation_percent, "ai_insight": ai_insight})


@app.route('/portfolio/regions', methods=['GET'])
def analyze_regions():
    """Analyzes regional diversification in the user's portfolio"""
    portfolio = user_data["user"]["portfolio"]
    
    region_allocation = {}
    for asset_type in ["stocks", "funds", "bonds"]:
        for asset in portfolio.get(asset_type, []):
            region = asset["region"]
            region_allocation[region] = region_allocation.get(region, 0) + asset["current_price"] * asset["quantity"]

    total_value = sum(region_allocation.values())
    region_percent = {k: (v / total_value) * 100 if total_value else 0 for k, v in region_allocation.items()}

    ai_insight = generate_ai_insight("regional diversification", region_allocation, region_percent)

    return jsonify({"regional_distribution": region_percent, "ai_insight": ai_insight})


@app.route('/portfolio/sectors', methods=['GET'])
def analyze_sectors():
    """Analyzes industry sector exposure in the user's portfolio"""
    portfolio = user_data["user"]["portfolio"]
    
    sector_allocation = {}
    for asset_type in ["stocks", "funds", "bonds"]:
        for asset in portfolio.get(asset_type, []):
            sector = asset["industry_sector"]
            sector_allocation[sector] = sector_allocation.get(sector, 0) + asset["current_price"] * asset["quantity"]

    total_value = sum(sector_allocation.values())
    sector_percent = {k: (v / total_value) * 100 if total_value else 0 for k, v in sector_allocation.items()}

    ai_insight = generate_ai_insight("industry sector diversification", sector_allocation, sector_percent)

    return jsonify({"sector_distribution": sector_percent, "ai_insight": ai_insight})


def generate_ai_insight(category, raw_data, percentages):
    """Generates AI insights for asset, regional, or sector analysis"""
    summary = (
        f"Investment Category: {category.capitalize()}\n"
        f"Raw Data Allocation: {raw_data}\n"
        f"Percentage Allocation: {percentages}\n"
    )

    if category == "asset allocation":
        # Prompt requesting structured output
        prompt = f"""
        {summary}
        
        Please provide the analysis in the following structured format as a JSON object:
        {{
            "summary": "two sentence overview of the allocation",
            "risk_assessment": "assest risk level for different assests",
            "balance_evaluation": "analysis diversification, overal risk level and liquidity",
            "suggestions": "give three suggestions to improve the portfolio"
        }}

        The data is about {category}, and the allocation is as follows:
        Raw Data: {raw_data}
        Percentage Data: {percentages}
        """
    
    if category == "regional diversification":
        # Prompt requesting structured output
        prompt = f"""
        {summary}
        
        Please provide the analysis in the following structured format as a JSON object:
        {{
            "summary": "Two sentence overview of the allocation",
            "regional_breakdown": "list all investments and the percentage",
            "comments_and_evaluation": "analysis diversification, overal risk level and liquidity",
            "regional_diversification": "analysis the divesrification of the portfolio",
            "evaluation": "analyse the strength and areas for improvement of the portfolio",
            "suggestions": "offer three suggestions to improve the portfolio"
        }}

        The data is about {category}, and the allocation is as follows:
        Raw Data: {raw_data}
        Percentage Data: {percentages}
        """
    
    if category == "industry sector diversification":
        # Prompt requesting structured output
        prompt = f"""
        {summary}
        
        Please provide the analysis in the following structured format as a JSON object:
        {{
            "summary": "Two sentence overview of the allocation",
            "sector_breakdown": "list all investments and the percentage",
            "comments_and_evaluation": "analysis diversification, overal risk level and liquidity",
            "regional_diversification": "analysis the divesrification of the portfolio",
            "evaluation": "analyse the strength and areas for improvement of the portfolio",
            "suggestions": "offer three suggestions to improve the portfolio"
        }}

        The data is about {category}, and the allocation is as follows:
        Raw Data: {raw_data}
        Percentage Data: {percentages}
        """

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a financial analyst providing structured insights on investment allocation."},
                {"role": "user", "content": prompt}
            ]
        )
        
        # Assuming the response is a structured JSON, parse it
        return response.choices[0].message.content

    except Exception as e:
        return f"AI analysis unavailable: {str(e)}"

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
        ai_response = generate_ai_insight_stock(stock_symbol, stock_data)

    except Exception as e:
        return jsonify({'error': f'Error fetching data for {stock_symbol}: {str(e)}'}), 500

    return jsonify({'stock_data': stock_data, 'ai_insight': ai_response})

def generate_ai_insight_stock(symbol, stock_data):
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

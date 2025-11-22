from flask import Flask, render_template_string, request, redirect, url_for
import pandas as pd
import numpy as np
import sys
import os
import base64

app = Flask(__name__)

def get_img_as_base64(file_path):
    try:
        with open(file_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except:
        return ""

# Load datasets
def load_datasets():
    """Load stock prediction datasets"""
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        dataset_dir = os.path.join(base_dir, "..", "dataset")
        
        sp500_df = pd.read_csv(os.path.join(dataset_dir, "sp500.csv"))
        depression_df = pd.read_csv(os.path.join(dataset_dir, "depression_index.csv"))
        rainfall_df = pd.read_csv(os.path.join(dataset_dir, "rainfall.csv"))
        
        return sp500_df, depression_df, rainfall_df
    except Exception as e:
        print(f"Error loading datasets: {e}")
        return None, None, None

# Calculate metrics
sp500_df, depression_df, rainfall_df = load_datasets()

total_days = len(sp500_df) if sp500_df is not None else 0
date_range = f"2014-2024" if sp500_df is not None else "N/A"
features_count = 8  # S&P500 metrics + depression index + rainfall

# Build metrics list for stock prediction platform
metrics_data = [
    {
        "label": "Trading Days",
        "value": f"{total_days:,}",
        "delta": "",
        "context": date_range,
    },
    {
        "label": "Data Sources",
        "value": "3",
        "delta": "",
        "context": "S&P500, Depression Index, Rainfall",
    },
    {
        "label": "Features",
        "value": f"{features_count}",
        "delta": "",
        "context": "Price, Volume, Volatility, External",
    },
]

@app.route('/')
def home():
    metric_cards = []
    for metric in metrics_data:
        label = str(metric.get("label", "")).strip()
        value = str(metric.get("value", "")).strip()
        delta_text = str(metric.get("delta", "")).strip()
        context_text = str(metric.get("context", "")).strip()
        
        trend_html = ""
        if delta_text:
            trend_class = "trend-up" if delta_text.startswith("+") else "trend-down"
            trend_icon = "↑" if delta_text.startswith("+") else "↓"
            trend_html = f'<span class="{trend_class}">{trend_icon} {delta_text}</span>'
        
        metric_cards.append(
            f'<div class="metric-card">'
            f'<div class="metric-label">{label}</div>'
            f'<div class="metric-value">{value}</div>'
            f'</div>'
        )

    hero_html = f"""
    <div class="hero-container">
        <div class="hero-bg-pattern"></div>
        <div class="hero-content">
            <div>
                <h1 class="hero-title">S&P 500 Stock Prediction Platform</h1>
                <p class="hero-description">
                    Advanced machine learning platform for stock market prediction and analysis.
                    Leverage multi-source data including market indicators, sentiment analysis, and environmental factors
                    to predict S&P 500 trends with state-of-the-art models.
                </p>
            </div>
            <div class="metrics-grid" style="display: flex; flex-direction: column; gap: 1rem; align-items: stretch;">
                {''.join(metric_cards)}
            </div>
        </div>
    </div>
    """

    navigation_cards = [
        {
            "title": "Data Overview",
            "description": "Explore S&P 500 historical data, depression index trends, and rainfall patterns. View data distributions, correlations, and time-series visualizations.",
            "button": "View Data Dashboard",
            "url": "/data-overview",
        },
        {
            "title": "Feature Engineering",
            "description": "Build and analyze predictive features from raw data. Create technical indicators, sentiment scores, and environmental factors for model training.",
            "button": "Open Feature Lab",
            "url": "/feature-engineering",
        },
        {
            "title": "Model Training",
            "description": "Train machine learning models including LSTM, Random Forest, and XGBoost. Monitor training metrics, compare model performance, and tune hyperparameters.",
            "button": "Launch Training Console",
            "url": "/training",
        },
        {
            "title": "Predictions & Analytics",
            "description": "Generate stock price predictions, analyze forecast accuracy, and explore model insights. Export predictions and performance reports.",
            "button": "View Predictions",
            "url": "/predictions",
        },
    ]

    nav_html = ""
    for card in navigation_cards:
        nav_html += f"""
        <div class="nav-card">
            <h4 class="nav-title">{card['title']}</h4>
            <p class="nav-desc">{card['description']}</p>
            <a href="{card['url']}" class="btn btn-primary">{card['button']}</a>
        </div>
        """

    # Load CSS
    css = ""
    try:
        css_path = os.path.join(os.path.dirname(__file__), "styles", "app.css")
        with open(css_path, "r", encoding="utf-8") as f:
            css = f.read()
    except:
        pass

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>S&P 500 Stock Prediction Platform</title>
        <style>{css}</style>
    </head>
    <body>
        {hero_html}
        <div style="display: flex; gap: 1rem; flex-wrap: wrap;">
            {nav_html}
        </div>
    </body>
    </html>
    """
    return html

@app.route('/data-overview')
def data_overview():
    """Data overview page showing dataset statistics and visualizations"""
    sp500_df, depression_df, rainfall_df = load_datasets()
    
    if sp500_df is None:
        return "Error loading datasets"
    
    # Calculate statistics
    latest_close = sp500_df['Close_^GSPC'].iloc[-1]
    start_close = sp500_df['Close_^GSPC'].iloc[0]
    total_return = ((latest_close - start_close) / start_close) * 100
    avg_daily_return = sp500_df['Return'].mean() * 100
    avg_volatility = sp500_df['Volatility_7'].mean() * 100
    
    stats_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Data Overview - Stock Prediction</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
            .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }}
            h1 {{ color: #2c3e50; }}
            .stat-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 30px 0; }}
            .stat-card {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; }}
            .stat-label {{ font-size: 14px; opacity: 0.9; }}
            .stat-value {{ font-size: 32px; font-weight: bold; margin: 10px 0; }}
            .back-btn {{ display: inline-block; padding: 10px 20px; background: #3498db; color: white; text-decoration: none; border-radius: 5px; margin-bottom: 20px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <a href="/" class="back-btn">← Back to Home</a>
            <h1>📊 Data Overview</h1>
            <div class="stat-grid">
                <div class="stat-card">
                    <div class="stat-label">Latest S&P 500 Close</div>
                    <div class="stat-value">${latest_close:,.2f}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Total Return (Period)</div>
                    <div class="stat-value">{total_return:+.2f}%</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Avg Daily Return</div>
                    <div class="stat-value">{avg_daily_return:+.3f}%</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Avg 7-Day Volatility</div>
                    <div class="stat-value">{avg_volatility:.2f}%</div>
                </div>
            </div>
            <h2>Dataset Information</h2>
            <p><strong>S&P 500 Data:</strong> {len(sp500_df):,} trading days from {sp500_df['Date'].iloc[0]} to {sp500_df['Date'].iloc[-1]}</p>
            <p><strong>Depression Index:</strong> {len(depression_df):,} weekly observations</p>
            <p><strong>Rainfall Data:</strong> {len(rainfall_df):,} daily records across 50 US states</p>
        </div>
    </body>
    </html>
    """
    return stats_html

@app.route('/feature-engineering')
def feature_engineering():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Feature Engineering - Stock Prediction</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }
            h1 { color: #2c3e50; }
            .back-btn { display: inline-block; padding: 10px 20px; background: #3498db; color: white; text-decoration: none; border-radius: 5px; margin-bottom: 20px; }
            .feature-list { list-style: none; padding: 0; }
            .feature-list li { padding: 15px; margin: 10px 0; background: #ecf0f1; border-radius: 5px; border-left: 4px solid #3498db; }
        </style>
    </head>
    <body>
        <div class="container">
            <a href="/" class="back-btn">← Back to Home</a>
            <h1>🔧 Feature Engineering</h1>
            <h2>Available Features</h2>
            <ul class="feature-list">
                <li><strong>Price Features:</strong> Open, High, Low, Close, Volume</li>
                <li><strong>Technical Indicators:</strong> Returns, 7-day Volatility</li>
                <li><strong>Sentiment:</strong> Depression Index (Google Trends)</li>
                <li><strong>Environmental:</strong> Rainfall patterns by state</li>
                <li><strong>Derived Features:</strong> Moving averages, momentum indicators (to be implemented)</li>
            </ul>
        </div>
    </body>
    </html>
    """

@app.route('/training')
def training():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Model Training - Stock Prediction</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }
            h1 { color: #2c3e50; }
            .back-btn { display: inline-block; padding: 10px 20px; background: #3498db; color: white; text-decoration: none; border-radius: 5px; margin-bottom: 20px; }
            .model-card { background: #f8f9fa; padding: 20px; margin: 15px 0; border-radius: 8px; border-left: 4px solid #28a745; }
            .model-name { font-size: 20px; font-weight: bold; color: #2c3e50; margin-bottom: 10px; }
            .model-desc { color: #555; line-height: 1.6; }
        </style>
    </head>
    <body>
        <div class="container">
            <a href="/" class="back-btn">← Back to Home</a>
            <h1>🤖 Model Training</h1>
            <p>Train machine learning models for stock price prediction</p>
            
            <div class="model-card">
                <div class="model-name">LSTM (Long Short-Term Memory)</div>
                <div class="model-desc">Deep learning model ideal for time-series prediction. Captures long-term dependencies in sequential data.</div>
            </div>
            
            <div class="model-card">
                <div class="model-name">Random Forest</div>
                <div class="model-desc">Ensemble learning method combining multiple decision trees for robust predictions.</div>
            </div>
            
            <div class="model-card">
                <div class="model-name">XGBoost</div>
                <div class="model-desc">Gradient boosting framework optimized for speed and performance.</div>
            </div>
            
            <div class="model-card">
                <div class="model-name">Linear Regression</div>
                <div class="model-desc">Baseline model for comparison and understanding feature relationships.</div>
            </div>
        </div>
    </body>
    </html>
    """

@app.route('/predictions')
def predictions():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Predictions & Analytics - Stock Prediction</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }
            h1 { color: #2c3e50; }
            .back-btn { display: inline-block; padding: 10px 20px; background: #3498db; color: white; text-decoration: none; border-radius: 5px; margin-bottom: 20px; }
            .info-box { background: #e3f2fd; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #2196f3; }
        </style>
    </head>
    <body>
        <div class="container">
            <a href="/" class="back-btn">← Back to Home</a>
            <h1>📈 Predictions & Analytics</h1>
            <div class="info-box">
                <h3>Coming Soon</h3>
                <p>This section will display:</p>
                <ul>
                    <li>Real-time stock price predictions</li>
                    <li>Model performance metrics (MAE, RMSE, R²)</li>
                    <li>Prediction confidence intervals</li>
                    <li>Feature importance analysis</li>
                    <li>Historical accuracy charts</li>
                </ul>
            </div>
        </div>
    </body>
    </html>
    """

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=18502)
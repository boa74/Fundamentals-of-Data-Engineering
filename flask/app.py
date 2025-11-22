from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import numpy as np
import sys
import os
import base64
import json
from pymongo import MongoClient
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__, template_folder='templates')

# Enable template auto-reload for development
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Database connections
mongo_host = os.getenv('MONGO_HOST', 'localhost')
mongo_port = os.getenv('MONGO_PORT', '37017')
mongo_db_name = os.getenv('MONGO_DB', 'db')
mongo_user = os.getenv('MONGO_USER')
mongo_password = os.getenv('MONGO_PASSWORD')

# Only use authentication if both user and password are provided
if mongo_user and mongo_password:
    mongo_uri = f'mongodb://{mongo_user}:{mongo_password}@{mongo_host}:{mongo_port}/{mongo_db_name}'
else:
    mongo_uri = f'mongodb://{mongo_host}:{mongo_port}/{mongo_db_name}'

try:
    mongo_client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
    mongo_db = mongo_client[mongo_db_name]
    # Test the connection
    mongo_client.admin.command('ping')
    print("MongoDB connection successful")
except Exception as e:
    print(f"MongoDB connection failed: {e}")
    # Fallback for local development
    if mongo_host != 'localhost':
        print("Trying localhost connection...")
        try:
            mongo_client = MongoClient('mongodb://localhost:37017/db', serverSelectionTimeoutMS=5000)
            mongo_db = mongo_client['db']
            mongo_client.admin.command('ping')
            print("Localhost MongoDB connection successful")
        except Exception as e2:
            print(f"Localhost connection also failed: {e2}")
            mongo_client = None
            mongo_db = None

# PostgreSQL connection
def get_postgres_connection():
    host = os.getenv('POSTGRES_HOST', 'localhost')
    port = os.getenv('POSTGRES_PORT', '45432')
    database = os.getenv('POSTGRES_DB', 'db')
    user = os.getenv('POSTGRES_USER', 'admin')
    password = os.getenv('POSTGRES_PASSWORD', 'PassW0rd')
    
    return psycopg2.connect(
        host=host,
        port=port,
        database=database,
        user=user,
        password=password
    )

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
    {
        "title": "Query MongoDB",
        "description": "Query and explore your imported datasets stored in MongoDB. Execute custom queries, view collections, and analyze NoSQL data structures.",
        "button": "Open MongoDB Query",
        "url": "/query-mongodb",
    },
    {
        "title": "Query PostgreSQL",
        "description": "Execute SQL queries on your PostgreSQL database. Browse tables, run analytics queries, and extract insights from relational data.",
        "button": "Open PostgreSQL Query",
        "url": "/query-postgresql",
    },
]

@app.route('/')
def home():
    return render_template('home.html', metrics_data=metrics_data, navigation_cards=navigation_cards)

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
    
    return render_template('data_overview.html',
                          latest_close=latest_close,
                          total_return=total_return,
                          avg_daily_return=avg_daily_return,
                          avg_volatility=avg_volatility,
                          sp500_count=len(sp500_df),
                          sp500_start=sp500_df['Date'].iloc[0],
                          sp500_end=sp500_df['Date'].iloc[-1],
                          depression_count=len(depression_df),
                          rainfall_count=len(rainfall_df))

@app.route('/feature-engineering')
def feature_engineering():
    return render_template('feature_engineering.html')

@app.route('/training')
def training():
    return render_template('training.html')

@app.route('/predictions')
def predictions():
    return render_template('predictions.html')

@app.route('/import-summary')
def import_summary():
    import os
    import json
    summary_file = os.path.join(os.path.dirname(__file__), 'import_summary.json')
    if os.path.exists(summary_file):
        with open(summary_file, 'r') as f:
            summary = json.load(f)
        return render_template('import_summary.html', summary=summary)
    else:
        return "Import summary not found. Please run the import script first."

@app.route('/query-mongodb', methods=['GET', 'POST'])
def query_mongodb():
    collections = mongo_db.list_collection_names()
    results = None
    error = None
    
    if request.method == 'POST':
        collection_name = request.form.get('collection')
        query = request.form.get('query', '{}')
        limit = int(request.form.get('limit', 10))
        
        try:
            collection = mongo_db[collection_name]
            # Parse query as JSON
            query_dict = json.loads(query) if query.strip() else {}
            cursor = collection.find(query_dict).limit(limit)
            results = list(cursor)
            
            # Convert ObjectId to string for JSON serialization
            for doc in results:
                if '_id' in doc:
                    doc['_id'] = str(doc['_id'])
                    
        except Exception as e:
            error = str(e)
    
    return render_template('query_mongodb.html', 
                         collections=collections, 
                         results=results, 
                         error=error)

@app.route('/query-postgresql', methods=['GET', 'POST'])
def query_postgresql():
    results = None
    columns = None
    error = None
    
    if request.method == 'POST':
        query = request.form.get('query', '').strip()
        
        # Basic safety check - only allow SELECT queries
        if not query.upper().startswith('SELECT'):
            error = "Only SELECT queries are allowed for security reasons."
        else:
            try:
                conn = get_postgres_connection()
                cursor = conn.cursor(cursor_factory=RealDictCursor)
                cursor.execute(query)
                results = cursor.fetchall()
                columns = list(results[0].keys()) if results else []
                cursor.close()
                conn.close()
            except Exception as e:
                error = str(e)
    
    return render_template('query_postgresql.html', 
                         results=results, 
                         columns=columns, 
                         error=error)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=18502, debug=True)
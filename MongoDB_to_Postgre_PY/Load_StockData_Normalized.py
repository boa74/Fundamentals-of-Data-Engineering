# ============================================================================
# LOAD STOCK DATA IN NORMALIZED FORMAT (LONG FORMAT)
# ============================================================================
# This script converts wide-format stock data (2511 columns) into normalized
# long-format (7 columns) so it can fit in PostgreSQL and be easily queried.
#
# WIDE FORMAT (Original - TOO MANY COLUMNS):
#   Date       | Open_AAPL | High_AAPL | Low_AAPL | ... (2511 columns total)
#   2014-01-01 | 100.5     | 101.2     | 99.8     | ...
#
# LONG FORMAT (Normalized - DATABASE FRIENDLY):
#   date       | ticker | open  | high  | low   | close | volume
#   2014-01-01 | AAPL   | 100.5 | 101.2 | 99.8  | 100.9 | 1000000
#   2014-01-01 | MSFT   | 45.2  | 45.8  | 44.9  | 45.5  | 500000
# ============================================================================

# Import required libraries
from pymongo import MongoClient  # To connect to MongoDB database
import pandas as pd              # For data manipulation and analysis
from sqlalchemy import create_engine  # To connect to PostgreSQL database

# ============================================================================
# STEP 1: CONNECT TO MONGODB
# ============================================================================
# Create a connection to MongoDB running on localhost at port 27017
client = MongoClient('localhost', 27017)

# Access the 'tutorial' database inside MongoDB
db = client.tutorial

# ============================================================================
# STEP 2: CONFIGURE POSTGRESQL CONNECTION
# ============================================================================
# Define PostgreSQL connection parameters
PG_USER = 'postgres'      # PostgreSQL username
PG_PASSWORD = '123'       # PostgreSQL password
DB_NAME = 'tutorial_db'   # Database name where we'll store the data

# Create SQLAlchemy engine - this is a connection factory that manages
# database connections using a connection string format:
# postgresql://username:password@host:port/database_name
pg_engine = create_engine(f'postgresql://{PG_USER}:{PG_PASSWORD}@localhost:5432/{DB_NAME}')

# ============================================================================
# STEP 3: EXTRACT DATA FROM MONGODB
# ============================================================================
print("Loading StockData from MongoDB...")

# Get reference to the 'StockData' collection in MongoDB
col_3 = db.StockData

# Find all documents in the collection
# {"_id": 0} means exclude the MongoDB internal _id field
# list() converts the MongoDB cursor to a Python list
docs_3 = list(col_3.find({}, {"_id": 0}))

# Convert list of dictionaries to pandas DataFrame
# DataFrame is like an Excel spreadsheet - rows and columns of data
df_3 = pd.DataFrame(docs_3)

# Clean the Date column:
# 1. pd.to_datetime() converts strings to proper datetime objects
# 2. .dt.strftime("%Y-%m-%d") formats dates as "YYYY-MM-DD" (e.g., "2014-01-01")
df_3["Date"] = pd.to_datetime(df_3["Date"]).dt.strftime("%Y-%m-%d")

# Display the original data structure
print(f"Original shape: {df_3.shape}")  # shape = (rows, columns), e.g., (4019, 2511)
print(f"Columns: {df_3.columns.tolist()[:10]}...")  # Show first 10 column names

# ============================================================================
# STEP 4: TRANSFORM FROM WIDE TO LONG FORMAT (NORMALIZATION)
# ============================================================================
print("\nTransforming to normalized format...")

# Get all column names except 'Date'
# These are stock-related columns like 'Open_AAPL', 'High_AAPL', 'Close_MSFT', etc.
stock_cols = [col for col in df_3.columns if col != 'Date']

# Create an empty list to store our normalized records
# Each record will be one row: {date, ticker, open, high, low, close, volume}
records = []

# Loop through each row in the original DataFrame
# idx = row number (0, 1, 2, ...), row = the actual data for that row
for idx, row in df_3.iterrows():
    # Get the date for this row
    date = row['Date']
    
    # ========================================================================
    # STEP 4A: FIND ALL UNIQUE TICKERS IN THIS ROW
    # ========================================================================
    # We need to figure out which stocks are represented in the columns
    # Example: If we have 'Open_AAPL', 'High_AAPL', 'Open_MSFT', 'High_MSFT'
    # We want to extract: {'AAPL', 'MSFT'}
    
    tickers = set()  # Use a set to automatically avoid duplicates
    
    for col in stock_cols:
        # Split column name by underscore
        # Example: "Open_AAPL" -> ["Open", "AAPL"]
        # Example: "High_MSFT" -> ["High", "MSFT"]
        parts = col.split('_')
        
        # If we have at least 2 parts (metric_ticker format)
        if len(parts) >= 2:
            # The ticker is always the last part after the underscore
            # parts[-1] means "last item in the list"
            tickers.add(parts[-1])  # Add ticker to our set
    
    # ========================================================================
    # STEP 4B: CREATE ONE RECORD PER TICKER
    # ========================================================================
    # Now for each ticker, collect all its data (open, high, low, close, volume)
    # from this row and create a normalized record
    
    for ticker in tickers:
        # Create a dictionary for this ticker on this date
        # We look up values using the column naming pattern: Metric_Ticker
        record = {
            'date': date,                                    # Same date for all tickers in this row
            'ticker': ticker,                                # Stock ticker (e.g., 'AAPL')
            'open': row.get(f'Open_{ticker}'),              # Opening price (e.g., value from 'Open_AAPL' column)
            'high': row.get(f'High_{ticker}'),              # Highest price during the day
            'low': row.get(f'Low_{ticker}'),                # Lowest price during the day
            'close': row.get(f'Close_{ticker}'),            # Closing price
            'volume': row.get(f'Volume_{ticker}')           # Number of shares traded
        }
        
        # row.get() is safer than row[] because it returns None if column doesn't exist
        # instead of throwing an error
        
        # Add this record to our list
        records.append(record)
    
    # Print progress every 100 rows so we know the script is working
    if (idx + 1) % 100 == 0:
        print(f"  Processed {idx + 1} rows...")

# ============================================================================
# STEP 5: CREATE NORMALIZED DATAFRAME
# ============================================================================
# Convert our list of dictionaries into a new DataFrame
# Now instead of 2511 columns, we have only 7 columns!
df_normalized = pd.DataFrame(records)

# Show the transformation results
print(f"\nNormalized shape: {df_normalized.shape}")  # Should be (~2 million rows, 7 columns)
print(df_normalized.head(10))  # Display first 10 rows to verify structure

# ============================================================================
# STEP 6: SEND TO POSTGRESQL
# ============================================================================
print("\nSending to PostgreSQL...")

# Open a connection to PostgreSQL
# 'with' statement automatically closes connection when done (good practice!)
with pg_engine.connect() as conn:
    # Write DataFrame to SQL table
    # Parameters:
    #   'stock_data' = name of the table to create
    #   conn = database connection
    #   if_exists='replace' = drop table if it exists and create new one
    #   index=False = don't include DataFrame index as a column
    #   method='multi' = insert multiple rows at once (faster!)
    #   chunksize=5000 = insert 5000 rows at a time (prevents memory issues)
    df_normalized.to_sql('stock_data', conn, if_exists='replace', index=False, method='multi', chunksize=5000)

print("✓ stock_data table created successfully!")

# ============================================================================
# STEP 7: DISPLAY SUMMARY STATISTICS
# ============================================================================
print("\nTable structure:")
print(f"  Columns: date, ticker, open, high, low, close, volume")
print(f"  Total records: {len(df_normalized):,}")  # :, adds commas to number (e.g., 2,017,538)
print(f"  Unique tickers: {df_normalized['ticker'].nunique()}")  # Count distinct tickers
print(f"  Date range: {df_normalized['date'].min()} to {df_normalized['date'].max()}")  # First to last date

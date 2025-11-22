# ============================================================================
# COUNT "DEPRESSION" MENTIONS IN NEWS ARTICLES BY DATE
# ============================================================================
# This script analyzes the ccnews_depression table and counts how many times
# the word "depression" appears in news articles (title + text) on each date.
#
# OUTPUT: Creates a CSV file with daily depression word counts
# ============================================================================

# Import required libraries
import pandas as pd
import psycopg2
from sqlalchemy import create_engine
import re

# ============================================================================
# STEP 1: CONFIGURE POSTGRESQL CONNECTION
# ============================================================================
PG_USER = 'postgres'
PG_PASSWORD = '123'
DB_NAME = 'tutorial_db'

# Create database connection engine
pg_engine = create_engine(f'postgresql://{PG_USER}:{PG_PASSWORD}@localhost:5432/{DB_NAME}')

print("Connecting to PostgreSQL...")
print("=" * 70)

# ============================================================================
# STEP 2: LOAD NEWS DATA FROM POSTGRESQL
# ============================================================================
print("\nLoading ccnews_depression data from PostgreSQL...")

# Read the ccnews_depression table using psycopg2 connection
conn = psycopg2.connect(
    host="localhost",
    database=DB_NAME,
    user=PG_USER,
    password=PG_PASSWORD
)

query = "SELECT date, title, text FROM ccnews_depression"
df_news = pd.read_sql_query(query, conn)

# Convert date to datetime
df_news['date'] = pd.to_datetime(df_news['date'], errors='coerce')

print(f"✓ Loaded {len(df_news):,} news articles")
if len(df_news) > 0 and df_news['date'].notna().any():
    print(f"Date range: {df_news['date'].min()} to {df_news['date'].max()}")
else:
    print("No data found in ccnews_depression table")
    
conn.close()

# ============================================================================
# STEP 3: COUNT "DEPRESSION" MENTIONS IN EACH ARTICLE
# ============================================================================
print("\nCounting 'depression' mentions in each article...")

def count_depression(text):
    """
    Count how many times the word 'depression' appears in the text.
    Case-insensitive search.
    
    Args:
        text: String to search in
        
    Returns:
        Integer count of 'depression' occurrences
    """
    if pd.isna(text) or text is None:
        return 0
    
    # Convert to lowercase for case-insensitive matching
    text_lower = str(text).lower()
    
    # Use regex to find whole word matches (not partial matches)
    # \b means word boundary - so "depressing" won't match
    pattern = r'\bdepression\b'
    matches = re.findall(pattern, text_lower)
    
    return len(matches)

# Count depression mentions in both title and text
print("  Counting in titles...")
df_news['depression_count_title'] = df_news['title'].apply(count_depression)

print("  Counting in article text...")
df_news['depression_count_text'] = df_news['text'].apply(count_depression)

# Total count per article
df_news['depression_count_total'] = (df_news['depression_count_title'] + 
                                      df_news['depression_count_text'])

print(f"✓ Counting complete")
print(f"  Total 'depression' mentions found: {df_news['depression_count_total'].sum():,}")

# ============================================================================
# STEP 4: AGGREGATE BY DATE (ENSURING NO DUPLICATES)
# ============================================================================
print("\nAggregating counts by date...")

# Convert date column to datetime format
df_news['date'] = pd.to_datetime(df_news['date'], errors='coerce')

# Remove any duplicate articles (same date, title, text)
print(f"  Before deduplication: {len(df_news):,} articles")
df_news = df_news.drop_duplicates(subset=['date', 'title', 'text'], keep='first')
print(f"  After deduplication: {len(df_news):,} articles")

# Group by date and aggregate properly
daily_counts = df_news.groupby('date').agg({
    'depression_count_total': 'sum',         # Total depression mentions per day
    'date': 'count'                          # Number of articles per day
}).rename(columns={'date': 'article_count'})

# Reset index to make 'date' a regular column
daily_counts = daily_counts.reset_index()

# Rename columns for clarity
daily_counts.columns = ['date', 'depression_word_count', 'total_articles']

# Calculate average mentions per article
daily_counts['avg_depression_per_article'] = (
    daily_counts['depression_word_count'] / daily_counts['total_articles']
).round(2)

# Sort by date
daily_counts = daily_counts.sort_values('date')

# Format date as YYYY-MM-DD string
daily_counts['date'] = daily_counts['date'].dt.strftime('%Y-%m-%d')

# Verify no duplicate dates in final output
print(f"\n  Unique dates in output: {daily_counts['date'].nunique()}")
print(f"  Total rows in output: {len(daily_counts)}")
if daily_counts['date'].nunique() == len(daily_counts):
    print("  ✓ No duplicate dates in aggregated data")
else:
    print("  ⚠ Warning: Duplicate dates detected!")

print(f"✓ Aggregated data for {len(daily_counts)} unique dates")

# ============================================================================
# STEP 5: DISPLAY SUMMARY STATISTICS
# ============================================================================
print("\n" + "=" * 70)
print("SUMMARY STATISTICS")
print("=" * 70)
print(f"Total dates: {len(daily_counts)}")
print(f"Total articles analyzed: {daily_counts['total_articles'].sum():,}")
print(f"Total 'depression' mentions: {daily_counts['depression_word_count'].sum():,}")
print(f"Average mentions per day: {daily_counts['depression_word_count'].mean():.2f}")
print(f"Max mentions in a day: {daily_counts['depression_word_count'].max()}")
print(f"Date with most mentions: {daily_counts.loc[daily_counts['depression_word_count'].idxmax(), 'date']}")

# Show sample of the data
print("\nSample data (first 10 rows):")
print(daily_counts.head(10).to_string(index=False))

# ============================================================================
# STEP 6: EXPORT TO CSV (FINAL VERSION WITHOUT DUPLICATES)
# ============================================================================
output_filename = 'ccnews_depression_daily_count_final.csv'

print(f"\nExporting to CSV: {output_filename}")
daily_counts.to_csv(output_filename, index=False, encoding='utf-8')

print(f"✓ CSV file created successfully!")
print(f"  Location: {output_filename}")
print(f"  Rows: {len(daily_counts)}")
print(f"  Columns: {', '.join(daily_counts.columns)}")
print(f"  ✓ Guaranteed: One row per unique date (no duplicates)")

# ============================================================================
# STEP 7: OPTIONAL - ALSO SAVE TO POSTGRESQL
# ============================================================================
print("\nSaving results back to PostgreSQL...")

table_name = 'depression_daily_count'

# Create a new connection for saving
conn_save = psycopg2.connect(
    host="localhost",
    database=DB_NAME,
    user=PG_USER,
    password=PG_PASSWORD
)

daily_counts.to_sql(table_name, conn_save, if_exists='replace', index=False)
conn_save.close()

print(f"✓ Table '{table_name}' created in PostgreSQL")

print("\n" + "=" * 70)
print("✅ COMPLETE!")
print("=" * 70)
print(f"CSV file: {output_filename}")
print(f"PostgreSQL table: {table_name}")
print("\nColumns in output:")
print("  - date: Date of the news articles (YYYY-MM-DD)")
print("  - depression_word_count: Total mentions of 'depression' that day")
print("  - total_articles: Number of articles published that day")
print("  - avg_depression_per_article: Average mentions per article")

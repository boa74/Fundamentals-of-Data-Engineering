# ============================================================================
# COUNT "DEPRESSION" MENTIONS IN NEWS ARTICLES BY DATE - FROM MONGODB
# ============================================================================
# This script extracts news data directly from MongoDB and counts how many 
# times the word "depression" appears in articles on a daily basis.
#
# OUTPUT: Creates a CSV file with daily depression word counts
# ============================================================================

# Import required libraries
from pymongo import MongoClient
import pandas as pd
import re

# ============================================================================
# STEP 1: CONNECT TO MONGODB
# ============================================================================
print("Connecting to MongoDB...")
print("=" * 70)

client = MongoClient('localhost', 27017)
db = client.tutorial

# ============================================================================
# STEP 2: LOAD NEWS DATA FROM MONGODB
# ============================================================================
print("\nLoading CCnews_Depression data from MongoDB...")

col_2 = db.CCnews_Depression
docs_2 = list(col_2.find({}, {"_id": 0, "date": 1, "title": 1, "text": 1}))

# Convert to DataFrame
df_news = pd.DataFrame(docs_2)

print(f"✓ Loaded {len(df_news):,} news articles")

# Clean and format date
df_news["date"] = pd.to_datetime(df_news["date"], errors="coerce")

print(f"Date range: {df_news['date'].min()} to {df_news['date'].max()}")

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
# STEP 4: AGGREGATE BY DATE
# ============================================================================
print("\nAggregating counts by date...")

# Group by date and sum the counts (date is already datetime format)
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

print("\nSample data (last 10 rows):")
print(daily_counts.tail(10).to_string(index=False))

# ============================================================================
# STEP 6: EXPORT TO CSV
# ============================================================================
output_filename = 'ccnews_depression_daily_count.csv'

print(f"\nExporting to CSV: {output_filename}")
daily_counts.to_csv(output_filename, index=False, encoding='utf-8')

print(f"✓ CSV file created successfully!")
print(f"  Location: {output_filename}")
print(f"  Rows: {len(daily_counts)}")
print(f"  Columns: {', '.join(daily_counts.columns)}")

print("\n" + "=" * 70)
print("✅ COMPLETE!")
print("=" * 70)
print(f"CSV file: {output_filename}")
print("\nColumns in output:")
print("  - date: Date of the news articles (YYYY-MM-DD)")
print("  - depression_word_count: Total mentions of 'depression' that day")
print("  - total_articles: Number of articles published that day")
print("  - avg_depression_per_article: Average mentions per article")

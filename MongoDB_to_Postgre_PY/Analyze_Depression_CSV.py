# ============================================================================
# ANALYZE ccnews_depression_daily_count.csv FOR MISSING DATA
# ============================================================================

import pandas as pd
import numpy as np

print("=" * 80)
print("ANALYZING: ccnews_depression_daily_count.csv")
print("=" * 80)

# Load the CSV file
df = pd.read_csv('ccnews_depression_daily_count.csv')

print(f"\nBasic Info:")
print(f"  Total rows: {len(df):,}")
print(f"  Total columns: {len(df.columns)}")
print(f"  Columns: {list(df.columns)}")

# ============================================================================
# MISSING VALUE ANALYSIS
# ============================================================================
print("\n" + "=" * 80)
print("MISSING VALUE ANALYSIS")
print("=" * 80)

missing_summary = pd.DataFrame({
    'Column': df.columns,
    'Missing_Count': df.isnull().sum(),
    'Missing_Percentage': (df.isnull().sum() / len(df) * 100).round(2),
    'Data_Type': df.dtypes
})

print("\n" + missing_summary.to_string(index=False))

total_missing = df.isnull().sum().sum()
if total_missing > 0:
    print(f"\n⚠ Total missing values: {total_missing}")
else:
    print(f"\n✓ No missing values found!")

# ============================================================================
# DATA QUALITY CHECKS
# ============================================================================
print("\n" + "=" * 80)
print("DATA QUALITY CHECKS")
print("=" * 80)

# Check for duplicate dates
print(f"\n1. Duplicate Dates:")
duplicate_dates = df['date'].duplicated().sum()
if duplicate_dates > 0:
    print(f"  ⚠ {duplicate_dates} duplicate date entries found")
    print(f"\n  Sample duplicates:")
    dupes = df[df['date'].duplicated(keep=False)].sort_values('date')
    print(dupes.head(20).to_string(index=False))
else:
    print(f"  ✓ No duplicate dates")

# Check for duplicate rows
print(f"\n2. Duplicate Rows:")
duplicate_rows = df.duplicated().sum()
if duplicate_rows > 0:
    print(f"  ⚠ {duplicate_rows} duplicate rows")
else:
    print(f"  ✓ No duplicate rows")

# Check date coverage
print(f"\n3. Date Coverage:")
df['date_parsed'] = pd.to_datetime(df['date'], errors='coerce')
date_min = df['date_parsed'].min()
date_max = df['date_parsed'].max()
print(f"  Date range: {date_min} to {date_max}")

# Calculate expected vs actual dates
date_range = pd.date_range(start=date_min, end=date_max, freq='D')
expected_dates = len(date_range)
actual_unique_dates = df['date_parsed'].nunique()

print(f"  Expected days in range: {expected_dates}")
print(f"  Actual unique dates: {actual_unique_dates}")

if actual_unique_dates < expected_dates:
    missing_dates_count = expected_dates - actual_unique_dates
    print(f"  ⚠ Missing {missing_dates_count} dates in the range")
elif actual_unique_dates > expected_dates:
    print(f"  ⚠ More dates than expected - check for duplicates!")
else:
    print(f"  ✓ Complete date coverage (but may have duplicate timestamps)")

# Check for zero or negative values
print(f"\n4. Data Value Checks:")
zero_depression = (df['depression_word_count'] == 0).sum()
print(f"  Days with zero depression mentions: {zero_depression} ({(zero_depression/len(df)*100):.2f}%)")

zero_articles = (df['total_articles'] == 0).sum()
if zero_articles > 0:
    print(f"  ⚠ Days with zero articles: {zero_articles}")
else:
    print(f"  ✓ All days have at least one article")

# Statistical summary
print(f"\n5. Statistical Summary:")
print(df[['depression_word_count', 'total_articles', 'avg_depression_per_article']].describe().to_string())

# ============================================================================
# ISSUE: DUPLICATE DATES DETECTED
# ============================================================================
if duplicate_dates > 0:
    print("\n" + "=" * 80)
    print("⚠ ISSUE DETECTED: DUPLICATE DATES")
    print("=" * 80)
    print("\nThe dataset has multiple entries for the same date.")
    print("This likely happened because the data wasn't properly aggregated.")
    print("\nRECOMMENDATION: Aggregate by date to create one row per day.")
    
    # Show how many unique dates we have
    unique_dates = df['date_parsed'].nunique()
    print(f"\nCurrent rows: {len(df)}")
    print(f"Unique dates: {unique_dates}")
    print(f"Should be: {unique_dates} rows (one per date)")
    
    print("\n" + "=" * 80)
    print("CREATING PROPERLY AGGREGATED VERSION")
    print("=" * 80)
    
    # Properly aggregate by date
    df_aggregated = df.groupby('date').agg({
        'depression_word_count': 'sum',
        'total_articles': 'sum',
    }).reset_index()
    
    # Recalculate average
    df_aggregated['avg_depression_per_article'] = (
        df_aggregated['depression_word_count'] / df_aggregated['total_articles']
    ).round(2)
    
    # Sort by date
    df_aggregated['date_parsed'] = pd.to_datetime(df_aggregated['date'], errors='coerce')
    df_aggregated = df_aggregated.sort_values('date_parsed')
    df_aggregated = df_aggregated[['date', 'depression_word_count', 'total_articles', 'avg_depression_per_article']]
    
    print(f"\n✓ Aggregated to {len(df_aggregated)} unique dates")
    print("\nSample of corrected data:")
    print(df_aggregated.head(10).to_string(index=False))
    
    # Save corrected version
    output_file = 'ccnews_depression_daily_count_FIXED.csv'
    df_aggregated.to_csv(output_file, index=False)
    print(f"\n✓ Fixed version saved as: {output_file}")

# ============================================================================
# FINAL SUMMARY
# ============================================================================
print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)

if total_missing == 0 and duplicate_dates == 0:
    print("✅ Dataset is clean - no missing values or duplicate dates!")
elif total_missing > 0:
    print(f"⚠ Dataset has {total_missing} missing values - imputation needed")
    if duplicate_dates > 0:
        print(f"⚠ Dataset also has {duplicate_dates} duplicate dates - aggregation needed")
elif duplicate_dates > 0:
    print(f"⚠ Dataset has {duplicate_dates} duplicate dates")
    print(f"✓ No missing values")
    print(f"\n→ Use ccnews_depression_daily_count_FIXED.csv for analysis")

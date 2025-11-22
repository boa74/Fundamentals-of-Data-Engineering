# ============================================================================
# CHECK ccnews_depression_daily_count_FIXED.csv FOR MISSING VALUES
# ============================================================================

import pandas as pd
import numpy as np

print("=" * 80)
print("ANALYZING: ccnews_depression_daily_count_FIXED.csv")
print("=" * 80)

# Load the fixed CSV file
df = pd.read_csv('ccnews_depression_daily_count_FIXED.csv')

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
    print(f"\n✓ No NULL/NaN values found!")

# ============================================================================
# DATE GAP ANALYSIS
# ============================================================================
print("\n" + "=" * 80)
print("DATE COVERAGE ANALYSIS")
print("=" * 80)

# Parse dates
df['date_parsed'] = pd.to_datetime(df['date'], errors='coerce')

# Check for invalid dates
invalid_dates = df['date_parsed'].isnull().sum()
if invalid_dates > 0:
    print(f"\n⚠ Invalid dates found: {invalid_dates}")
else:
    print(f"\n✓ All dates are valid")

# Date range
date_min = df['date_parsed'].min()
date_max = df['date_parsed'].max()
print(f"\nDate range: {date_min.date()} to {date_max.date()}")

# Calculate date gaps
date_range = pd.date_range(start=date_min, end=date_max, freq='D')
expected_dates = len(date_range)
actual_dates = len(df)
missing_dates_count = expected_dates - actual_dates

print(f"Expected days in range: {expected_dates}")
print(f"Actual dates in file: {actual_dates}")

if missing_dates_count > 0:
    print(f"\n⚠ MISSING DATES: {missing_dates_count} days have no data")
    
    # Find which dates are missing
    existing_dates = set(df['date_parsed'].dt.date)
    all_dates = set(date_range.date)
    missing_dates = sorted(all_dates - existing_dates)
    
    print(f"\nFirst 20 missing dates:")
    for i, missing_date in enumerate(missing_dates[:20], 1):
        print(f"  {i}. {missing_date}")
    
    if len(missing_dates) > 20:
        print(f"  ... and {len(missing_dates) - 20} more missing dates")
    
    print(f"\nMissing dates percentage: {(missing_dates_count/expected_dates*100):.2f}%")
else:
    print(f"\n✓ Complete date coverage - no missing dates!")

# ============================================================================
# DATA QUALITY CHECKS
# ============================================================================
print("\n" + "=" * 80)
print("DATA QUALITY CHECKS")
print("=" * 80)

# Check for duplicates
duplicates = df.duplicated().sum()
duplicate_dates = df['date'].duplicated().sum()

if duplicates > 0:
    print(f"\n⚠ Duplicate rows: {duplicates}")
else:
    print(f"\n✓ No duplicate rows")

if duplicate_dates > 0:
    print(f"⚠ Duplicate dates: {duplicate_dates}")
else:
    print(f"✓ No duplicate dates")

# Check for zero or negative values
print(f"\nValue checks:")
zero_depression = (df['depression_word_count'] == 0).sum()
print(f"  Days with zero depression mentions: {zero_depression} ({(zero_depression/len(df)*100):.2f}%)")

negative_depression = (df['depression_word_count'] < 0).sum()
if negative_depression > 0:
    print(f"  ⚠ Days with negative depression count: {negative_depression}")
else:
    print(f"  ✓ No negative depression counts")

zero_articles = (df['total_articles'] == 0).sum()
if zero_articles > 0:
    print(f"  ⚠ Days with zero articles: {zero_articles}")
else:
    print(f"  ✓ All days have at least one article")

# Statistical summary
print(f"\n" + "=" * 80)
print("STATISTICAL SUMMARY")
print("=" * 80)
print(df[['depression_word_count', 'total_articles', 'avg_depression_per_article']].describe().to_string())

# ============================================================================
# FINAL ASSESSMENT
# ============================================================================
print("\n" + "=" * 80)
print("FINAL ASSESSMENT")
print("=" * 80)

issues = []
if total_missing > 0:
    issues.append(f"NULL values: {total_missing}")
if missing_dates_count > 0:
    issues.append(f"Missing dates: {missing_dates_count}")
if duplicates > 0:
    issues.append(f"Duplicate rows: {duplicates}")
if duplicate_dates > 0:
    issues.append(f"Duplicate dates: {duplicate_dates}")

if len(issues) == 0:
    print("\n✅ DATASET IS CLEAN!")
    print("   - No NULL values")
    print("   - No duplicate dates")
    print("   - No duplicate rows")
    print("   - Complete date coverage")
    print("\n   Ready for analysis!")
else:
    print("\n⚠ ISSUES FOUND:")
    for issue in issues:
        print(f"   - {issue}")
    
    if missing_dates_count > 0:
        print(f"\n📊 RECOMMENDATION:")
        print(f"   The dataset has {missing_dates_count} missing dates ({(missing_dates_count/expected_dates*100):.2f}%).")
        print(f"   Options:")
        print(f"   1. Use as-is (sparse time series)")
        print(f"   2. Fill missing dates with 0 counts")
        print(f"   3. Interpolate missing values")
        print(f"   4. Investigate why those dates are missing")

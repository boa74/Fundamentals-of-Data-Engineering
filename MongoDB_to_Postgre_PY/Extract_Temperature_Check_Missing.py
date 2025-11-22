# ============================================================================
# EXTRACT TEMPERATURE DATA FROM MONGODB AND CHECK FOR MISSING VALUES
# ============================================================================
# This script extracts temperature data from MongoDB, analyzes missing values,
# and exports to CSV for review.
# ============================================================================

from pymongo import MongoClient
import pandas as pd
import numpy as np

# ============================================================================
# STEP 1: CONNECT TO MONGODB
# ============================================================================
print("Connecting to MongoDB...")
print("=" * 70)

client = MongoClient('localhost', 27017)
db = client.tutorial

# List all collections to find temperature data
print("\nAvailable collections in MongoDB:")
collections = db.list_collection_names()
for i, col in enumerate(collections, 1):
    count = db[col].count_documents({})
    print(f"{i}. {col} ({count:,} documents)")

# ============================================================================
# STEP 2: EXTRACT TEMPERATURE DATA
# ============================================================================
# Check if there's a Temperature collection
if 'Temperature' in collections:
    collection_name = 'Temperature'
elif 'temperature' in collections:
    collection_name = 'temperature'
else:
    # Try to find any collection with temperature-related name
    temp_cols = [col for col in collections if 'temp' in col.lower()]
    if temp_cols:
        collection_name = temp_cols[0]
        print(f"\nFound temperature-related collection: {collection_name}")
    else:
        print("\n⚠ No temperature collection found!")
        print("Please specify the correct collection name.")
        exit()

print(f"\nExtracting data from '{collection_name}' collection...")

# Get the collection
col_temp = db[collection_name]

# Get a sample document to see the structure
sample_doc = col_temp.find_one()
if sample_doc:
    print(f"\nSample document structure:")
    for key in sample_doc.keys():
        print(f"  - {key}: {type(sample_doc[key]).__name__}")

# Extract all documents (excluding MongoDB's _id field)
docs = list(col_temp.find({}, {"_id": 0}))
df_temp = pd.DataFrame(docs)

print(f"\n✓ Loaded {len(df_temp):,} temperature records")
print(f"Columns: {list(df_temp.columns)}")

# ============================================================================
# STEP 3: ANALYZE MISSING VALUES
# ============================================================================
print("\n" + "=" * 70)
print("MISSING VALUE ANALYSIS")
print("=" * 70)

# Calculate missing values for each column
missing_stats = pd.DataFrame({
    'Column': df_temp.columns,
    'Missing_Count': df_temp.isnull().sum(),
    'Missing_Percentage': (df_temp.isnull().sum() / len(df_temp) * 100).round(2),
    'Data_Type': df_temp.dtypes.astype(str)
})

# Sort by missing count (highest first)
missing_stats = missing_stats.sort_values('Missing_Count', ascending=False)
missing_stats = missing_stats.reset_index(drop=True)

print("\nMissing Values Summary:")
print(missing_stats.to_string(index=False))

# Overall statistics
total_cells = df_temp.shape[0] * df_temp.shape[1]
total_missing = df_temp.isnull().sum().sum()
missing_pct = (total_missing / total_cells * 100)

print(f"\nOverall Statistics:")
print(f"  Total rows: {len(df_temp):,}")
print(f"  Total columns: {len(df_temp.columns)}")
print(f"  Total cells: {total_cells:,}")
print(f"  Total missing values: {total_missing:,}")
print(f"  Overall missing percentage: {missing_pct:.2f}%")

# Identify columns with missing values
cols_with_missing = missing_stats[missing_stats['Missing_Count'] > 0]['Column'].tolist()
print(f"\nColumns with missing values ({len(cols_with_missing)}):")
for col in cols_with_missing:
    missing_count = df_temp[col].isnull().sum()
    missing_pct = (missing_count / len(df_temp) * 100)
    print(f"  - {col}: {missing_count:,} ({missing_pct:.2f}%)")

# ============================================================================
# STEP 4: DATA QUALITY CHECKS
# ============================================================================
print("\n" + "=" * 70)
print("DATA QUALITY CHECKS")
print("=" * 70)

# Check for date column and analyze date coverage
date_cols = [col for col in df_temp.columns if 'date' in col.lower()]
if date_cols:
    date_col = date_cols[0]
    print(f"\nDate column found: '{date_col}'")
    
    # Convert to datetime
    df_temp[date_col] = pd.to_datetime(df_temp[date_col], errors='coerce')
    
    # Check for invalid dates
    invalid_dates = df_temp[date_col].isnull().sum()
    if invalid_dates > 0:
        print(f"  ⚠ Invalid dates found: {invalid_dates}")
    
    valid_dates = df_temp[df_temp[date_col].notna()]
    if len(valid_dates) > 0:
        print(f"  Date range: {valid_dates[date_col].min()} to {valid_dates[date_col].max()}")
        
        # Check for date gaps
        date_range = pd.date_range(start=valid_dates[date_col].min(), 
                                   end=valid_dates[date_col].max(), 
                                   freq='D')
        expected_dates = len(date_range)
        actual_dates = valid_dates[date_col].nunique()
        missing_dates = expected_dates - actual_dates
        
        if missing_dates > 0:
            print(f"  ⚠ Missing dates in range: {missing_dates} days")
        else:
            print(f"  ✓ Complete date coverage")

# Check for duplicate rows
duplicates = df_temp.duplicated().sum()
if duplicates > 0:
    print(f"\n⚠ Duplicate rows found: {duplicates}")
else:
    print(f"\n✓ No duplicate rows")

# Statistical summary for numeric columns
numeric_cols = df_temp.select_dtypes(include=[np.number]).columns.tolist()
if numeric_cols:
    print(f"\nNumeric columns summary:")
    print(df_temp[numeric_cols].describe().to_string())

# ============================================================================
# STEP 5: RECOMMENDATIONS
# ============================================================================
print("\n" + "=" * 70)
print("IMPUTATION RECOMMENDATIONS")
print("=" * 70)

if len(cols_with_missing) == 0:
    print("\n✓ No missing values found! Dataset is complete.")
else:
    print("\nBased on the analysis:")
    for col in cols_with_missing:
        missing_pct = (df_temp[col].isnull().sum() / len(df_temp) * 100)
        
        if missing_pct < 5:
            print(f"\n{col} ({missing_pct:.2f}% missing):")
            print(f"  → Low missing rate. Recommended: Forward fill or interpolation")
        elif missing_pct < 30:
            print(f"\n{col} ({missing_pct:.2f}% missing):")
            print(f"  → Moderate missing rate. Recommended: Mean/median imputation or interpolation")
        else:
            print(f"\n{col} ({missing_pct:.2f}% missing):")
            print(f"  → High missing rate. Recommended: Consider dropping column or advanced imputation")

# ============================================================================
# STEP 6: EXPORT TO CSV
# ============================================================================
output_filename = 'temperature_data_with_missing_analysis.csv'

print(f"\nExporting temperature data to CSV: {output_filename}")
df_temp.to_csv(output_filename, index=False, encoding='utf-8')

# Also export missing value summary
missing_summary_file = 'temperature_missing_value_summary.csv'
missing_stats.to_csv(missing_summary_file, index=False, encoding='utf-8')

print(f"✓ Data exported to: {output_filename}")
print(f"✓ Missing value summary exported to: {missing_summary_file}")

print("\n" + "=" * 70)
print("✅ ANALYSIS COMPLETE!")
print("=" * 70)
print(f"\nFiles created:")
print(f"  1. {output_filename} - Full temperature dataset")
print(f"  2. {missing_summary_file} - Missing value analysis")
print(f"\nYou can now review the data and decide on imputation strategy.")

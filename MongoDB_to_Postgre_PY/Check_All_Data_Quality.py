# ============================================================================
# COMPREHENSIVE DATA QUALITY CHECK FOR ALL MONGODB DATASETS
# ============================================================================
# This script analyzes ALL collections in MongoDB for missing values,
# data quality issues, and exports detailed reports.
# ============================================================================

from pymongo import MongoClient
import pandas as pd
import numpy as np
import os

# ============================================================================
# STEP 1: CONNECT TO MONGODB
# ============================================================================
print("=" * 80)
print("COMPREHENSIVE DATA QUALITY CHECK - ALL MONGODB COLLECTIONS")
print("=" * 80)

client = MongoClient('localhost', 27017)
db = client.tutorial

# Get all collections
collections = db.list_collection_names()
print(f"\nFound {len(collections)} collections in MongoDB:")
for i, col in enumerate(collections, 1):
    count = db[col].count_documents({})
    print(f"  {i}. {col:30} ({count:,} documents)")

# Create output directory for reports
output_dir = 'data_quality_reports'
os.makedirs(output_dir, exist_ok=True)
print(f"\nReports will be saved to: {output_dir}/")

# ============================================================================
# STEP 2: ANALYZE EACH COLLECTION
# ============================================================================
all_summaries = []

for collection_name in collections:
    print("\n" + "=" * 80)
    print(f"ANALYZING: {collection_name}")
    print("=" * 80)
    
    # Get collection
    col = db[collection_name]
    
    # Extract data
    docs = list(col.find({}, {"_id": 0}))
    
    if len(docs) == 0:
        print(f"  ⚠ Empty collection - skipping")
        continue
    
    df = pd.DataFrame(docs)
    
    print(f"\nBasic Info:")
    print(f"  Rows: {len(df):,}")
    print(f"  Columns: {len(df.columns)}")
    print(f"  Column names: {list(df.columns)}")
    
    # ========================================================================
    # MISSING VALUE ANALYSIS
    # ========================================================================
    print(f"\nMissing Value Analysis:")
    
    missing_info = []
    for col_name in df.columns:
        null_count = df[col_name].isnull().sum()
        null_pct = (null_count / len(df) * 100)
        
        # Also check for empty strings
        if df[col_name].dtype == 'object':
            empty_count = (df[col_name] == '').sum()
            empty_pct = (empty_count / len(df) * 100)
        else:
            empty_count = 0
            empty_pct = 0
        
        missing_info.append({
            'Collection': collection_name,
            'Column': col_name,
            'Data_Type': str(df[col_name].dtype),
            'Null_Count': null_count,
            'Null_Percentage': round(null_pct, 2),
            'Empty_String_Count': empty_count,
            'Empty_String_Percentage': round(empty_pct, 2),
            'Total_Missing': null_count + empty_count,
            'Total_Missing_Percentage': round(null_pct + empty_pct, 2)
        })
    
    missing_df = pd.DataFrame(missing_info)
    missing_df = missing_df.sort_values('Total_Missing', ascending=False)
    
    # Print missing value summary
    cols_with_issues = missing_df[missing_df['Total_Missing'] > 0]
    if len(cols_with_issues) > 0:
        print(f"  ⚠ Columns with missing data: {len(cols_with_issues)}")
        for _, row in cols_with_issues.iterrows():
            print(f"    - {row['Column']:30} {row['Total_Missing']:6} missing ({row['Total_Missing_Percentage']:6.2f}%)")
    else:
        print(f"  ✓ No missing values!")
    
    # ========================================================================
    # DATA QUALITY CHECKS
    # ========================================================================
    print(f"\nData Quality Checks:")
    
    # Check for duplicates
    duplicates = df.duplicated().sum()
    if duplicates > 0:
        print(f"  ⚠ Duplicate rows: {duplicates}")
    else:
        print(f"  ✓ No duplicate rows")
    
    # Check date columns
    date_cols = [col for col in df.columns if 'date' in col.lower()]
    if date_cols:
        for date_col in date_cols:
            print(f"\n  Date column '{date_col}':")
            df_temp = df.copy()
            df_temp[date_col] = pd.to_datetime(df_temp[date_col], errors='coerce')
            
            invalid_dates = df_temp[date_col].isnull().sum()
            valid_dates = df_temp[date_col].notna().sum()
            
            if invalid_dates > 0:
                print(f"    ⚠ Invalid dates: {invalid_dates}")
            
            if valid_dates > 0:
                date_min = df_temp[date_col].min()
                date_max = df_temp[date_col].max()
                print(f"    Range: {date_min} to {date_max}")
                
                # Check for date gaps (daily frequency)
                date_range = pd.date_range(start=date_min, end=date_max, freq='D')
                expected_dates = len(date_range)
                actual_dates = df_temp[date_col].nunique()
                missing_dates = expected_dates - actual_dates
                
                if missing_dates > 0:
                    print(f"    ⚠ Missing dates in range: {missing_dates} days")
                else:
                    print(f"    ✓ Complete date coverage")
    
    # Numeric columns statistics
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if numeric_cols:
        print(f"\n  Numeric columns ({len(numeric_cols)}):")
        for num_col in numeric_cols:
            print(f"    {num_col:30} min={df[num_col].min():.2f}, max={df[num_col].max():.2f}, mean={df[num_col].mean():.2f}")
    
    # ========================================================================
    # EXPORT INDIVIDUAL COLLECTION REPORT
    # ========================================================================
    # Export full data
    data_filename = os.path.join(output_dir, f'{collection_name}_data.csv')
    df.to_csv(data_filename, index=False, encoding='utf-8')
    print(f"\n  ✓ Data exported: {data_filename}")
    
    # Export missing value details
    missing_filename = os.path.join(output_dir, f'{collection_name}_missing_analysis.csv')
    missing_df.to_csv(missing_filename, index=False, encoding='utf-8')
    print(f"  ✓ Missing analysis: {missing_filename}")
    
    # Add to overall summary
    all_summaries.append({
        'Collection': collection_name,
        'Total_Rows': len(df),
        'Total_Columns': len(df.columns),
        'Columns_With_Missing': len(cols_with_issues),
        'Total_Missing_Values': missing_df['Total_Missing'].sum(),
        'Missing_Percentage': round((missing_df['Total_Missing'].sum() / (len(df) * len(df.columns)) * 100), 2),
        'Duplicate_Rows': duplicates,
        'Has_Date_Column': 'Yes' if date_cols else 'No'
    })

# ============================================================================
# STEP 3: CREATE COMPREHENSIVE SUMMARY REPORT
# ============================================================================
print("\n" + "=" * 80)
print("OVERALL SUMMARY - ALL COLLECTIONS")
print("=" * 80)

summary_df = pd.DataFrame(all_summaries)
print("\n" + summary_df.to_string(index=False))

# Export overall summary
summary_filename = os.path.join(output_dir, 'OVERALL_SUMMARY.csv')
summary_df.to_csv(summary_filename, index=False, encoding='utf-8')

# ============================================================================
# STEP 4: GENERATE RECOMMENDATIONS
# ============================================================================
print("\n" + "=" * 80)
print("RECOMMENDATIONS")
print("=" * 80)

for _, row in summary_df.iterrows():
    collection = row['Collection']
    missing_pct = row['Missing_Percentage']
    
    print(f"\n{collection}:")
    
    if missing_pct == 0:
        print(f"  ✓ No missing values - dataset is complete!")
    elif missing_pct < 5:
        print(f"  → {missing_pct}% missing - Low impact")
        print(f"     Recommendation: Forward fill, interpolation, or mean imputation")
    elif missing_pct < 20:
        print(f"  ⚠ {missing_pct}% missing - Moderate impact")
        print(f"     Recommendation: Careful imputation required (mean/median/mode or interpolation)")
    else:
        print(f"  ⚠⚠ {missing_pct}% missing - High impact!")
        print(f"     Recommendation: Consider advanced imputation or investigate data source")
    
    if row['Duplicate_Rows'] > 0:
        print(f"  ⚠ {row['Duplicate_Rows']} duplicate rows - recommend removal")

# ============================================================================
# STEP 5: FINAL SUMMARY
# ============================================================================
print("\n" + "=" * 80)
print("✅ ANALYSIS COMPLETE!")
print("=" * 80)

total_collections = len(all_summaries)
collections_with_issues = len(summary_df[summary_df['Missing_Percentage'] > 0])

print(f"\nAnalyzed {total_collections} collections")
print(f"Collections with missing data: {collections_with_issues}")
print(f"\nAll reports saved in: {os.path.abspath(output_dir)}/")
print(f"\nKey files:")
print(f"  - OVERALL_SUMMARY.csv - Summary of all collections")
print(f"  - [collection]_data.csv - Full data export for each collection")
print(f"  - [collection]_missing_analysis.csv - Detailed missing value analysis")

# ============================================================================
# COMPREHENSIVE STATISTICAL ANALYSIS FOR ALL DATASETS
# ============================================================================

from pymongo import MongoClient
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

print("=" * 80)
print("COMPREHENSIVE STATISTICAL ANALYSIS - ALL MONGODB DATASETS")
print("=" * 80)

# Connect to MongoDB
client = MongoClient('localhost', 27017)
db = client.tutorial

# Get all collections
collections = db.list_collection_names()

# Store all statistics
all_stats = []

for collection_name in collections:
    print("\n" + "=" * 80)
    print(f"DATASET: {collection_name}")
    print("=" * 80)
    
    # Extract data
    col = db[collection_name]
    docs = list(col.find({}, {"_id": 0}))
    
    if len(docs) == 0:
        print("  Empty collection - skipping")
        continue
    
    df = pd.DataFrame(docs)
    
    print(f"\nBasic Information:")
    print(f"  Total Records: {len(df):,}")
    print(f"  Total Columns: {len(df.columns)}")
    
    # Get numeric columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    if len(numeric_cols) > 0:
        print(f"\n📊 STATISTICAL SUMMARY FOR NUMERIC COLUMNS ({len(numeric_cols)} columns):")
        print("-" * 80)
        
        # Calculate statistics for each numeric column
        for col_name in numeric_cols[:10]:  # Show first 10 numeric columns
            print(f"\n{col_name}:")
            
            # Remove NaN values for calculation
            values = df[col_name].dropna()
            
            if len(values) == 0:
                print("  All values are missing")
                continue
            
            stats = {
                'Count': len(values),
                'Missing': df[col_name].isnull().sum(),
                'Mean': values.mean(),
                'Median': values.median(),
                'Std Dev': values.std(),
                'Variance': values.var(),
                'Min': values.min(),
                'Max': values.max(),
                'Range': values.max() - values.min(),
                '25th Percentile': values.quantile(0.25),
                '75th Percentile': values.quantile(0.75),
                'IQR': values.quantile(0.75) - values.quantile(0.25),
                'Skewness': values.skew(),
                'Kurtosis': values.kurtosis()
            }
            
            for stat_name, stat_value in stats.items():
                if stat_name in ['Count', 'Missing']:
                    print(f"  {stat_name:20} {int(stat_value):>15,}")
                else:
                    print(f"  {stat_name:20} {stat_value:>15,.2f}")
        
        if len(numeric_cols) > 10:
            print(f"\n  ... and {len(numeric_cols) - 10} more numeric columns")
            print(f"  (Full statistics saved to CSV report)")
    
    # Text/categorical columns
    text_cols = df.select_dtypes(include=['object']).columns.tolist()
    
    if len(text_cols) > 0:
        print(f"\n📝 TEXT/CATEGORICAL COLUMNS ({len(text_cols)} columns):")
        print("-" * 80)
        
        for col_name in text_cols[:5]:  # Show first 5 text columns
            print(f"\n{col_name}:")
            print(f"  Unique values: {df[col_name].nunique():,}")
            print(f"  Missing values: {df[col_name].isnull().sum():,}")
            
            # Show most common values
            if df[col_name].nunique() < 50:  # Only show if reasonable number
                top_values = df[col_name].value_counts().head(3)
                print(f"  Most common values:")
                for val, count in top_values.items():
                    print(f"    - {str(val)[:50]}: {count:,} ({count/len(df)*100:.1f}%)")
        
        if len(text_cols) > 5:
            print(f"\n  ... and {len(text_cols) - 5} more text columns")
    
    # Overall DataFrame statistics
    print(f"\n📈 OVERALL DATASET STATISTICS:")
    print("-" * 80)
    print(df.describe(include='all').to_string())
    
    # Save detailed statistics to individual CSV
    stats_df = df.describe(include='all').T
    stats_df['column'] = stats_df.index
    stats_df = stats_df.reset_index(drop=True)
    
    # Add variance and std for numeric columns
    if len(numeric_cols) > 0:
        variance_dict = df[numeric_cols].var().to_dict()
        stats_df['variance'] = stats_df['column'].map(variance_dict)
    
    output_file = f'statistics_{collection_name}.csv'
    stats_df.to_csv(output_file, index=False)
    print(f"\n✓ Detailed statistics saved to: {output_file}")

# ============================================================================
# CREATE SUMMARY COMPARISON TABLE
# ============================================================================
print("\n" + "=" * 80)
print("CROSS-DATASET COMPARISON SUMMARY")
print("=" * 80)

summary_data = []

for collection_name in collections:
    col = db[collection_name]
    docs = list(col.find({}, {"_id": 0}))
    
    if len(docs) == 0:
        continue
    
    df = pd.DataFrame(docs)
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    # Calculate overall statistics
    summary_data.append({
        'Dataset': collection_name,
        'Records': len(df),
        'Columns': len(df.columns),
        'Numeric_Columns': len(numeric_cols),
        'Text_Columns': len(df.select_dtypes(include=['object']).columns),
        'Total_Missing_Values': df.isnull().sum().sum(),
        'Missing_Percentage': round(df.isnull().sum().sum() / (len(df) * len(df.columns)) * 100, 2),
        'Avg_Mean': round(df[numeric_cols].mean().mean(), 2) if len(numeric_cols) > 0 else None,
        'Avg_StdDev': round(df[numeric_cols].std().mean(), 2) if len(numeric_cols) > 0 else None,
    })

summary_df = pd.DataFrame(summary_data)
print("\n" + summary_df.to_string(index=False))

# Save summary
summary_df.to_csv('ALL_DATASETS_STATISTICAL_SUMMARY.csv', index=False)
print(f"\n✓ Summary saved to: ALL_DATASETS_STATISTICAL_SUMMARY.csv")

print("\n" + "=" * 80)
print("✅ STATISTICAL ANALYSIS COMPLETE!")
print("=" * 80)
print("\nGenerated files:")
print("  - ALL_DATASETS_STATISTICAL_SUMMARY.csv (comparison table)")
print("  - statistics_[dataset].csv (detailed stats for each dataset)")

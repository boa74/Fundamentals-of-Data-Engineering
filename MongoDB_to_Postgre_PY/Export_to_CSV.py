# ============================================================================
# EXPORT POSTGRESQL TABLES TO CSV FILES FOR TEAM SHARING
# ============================================================================
# This script connects to PostgreSQL and exports each table as a separate
# CSV file that your team members can easily import into pgAdmin or other tools.
#
# OUTPUT: Creates individual CSV files for each table in the current directory
# ============================================================================

# Import required libraries
import pandas as pd                    # For data manipulation and CSV export
from sqlalchemy import create_engine   # To connect to PostgreSQL
import os                              # For file path operations

# ============================================================================
# STEP 1: CONFIGURE POSTGRESQL CONNECTION
# ============================================================================
# PostgreSQL connection credentials
PG_USER = 'postgres'
PG_PASSWORD = '123'
DB_NAME = 'tutorial_db'

# Create database connection engine
pg_engine = create_engine(f'postgresql://{PG_USER}:{PG_PASSWORD}@localhost:5432/{DB_NAME}')

# ============================================================================
# STEP 2: DEFINE OUTPUT DIRECTORY
# ============================================================================
# Create a folder to store all CSV files
output_dir = 'csv_exports'

# Create the directory if it doesn't exist
# exist_ok=True means don't raise error if directory already exists
os.makedirs(output_dir, exist_ok=True)

print(f"Exporting tables to '{output_dir}' folder...")
print("=" * 60)

# ============================================================================
# STEP 3: DEFINE TABLES TO EXPORT
# ============================================================================
# List of all tables in our database with descriptions
tables = [
    {
        'name': 'depression_index',
        'description': 'Depression index data by date',
        'filename': 'depression_index.csv'
    },
    {
        'name': 'ccnews_depression',
        'description': 'News articles related to depression',
        'filename': 'ccnews_depression.csv'
    },
    {
        'name': 'stock_data',
        'description': 'Stock market data (normalized format)',
        'filename': 'stock_data.csv'
    },
    {
        'name': 'sp500',
        'description': 'S&P 500 index data',
        'filename': 'sp500.csv'
    },
    {
        'name': 'rainfall',
        'description': 'Rainfall data by US state',
        'filename': 'rainfall.csv'
    }
]

# ============================================================================
# STEP 4: EXPORT EACH TABLE TO CSV
# ============================================================================
# Keep track of export statistics
total_tables = len(tables)
successful_exports = 0
failed_exports = 0

# Loop through each table and export it
for table_info in tables:
    table_name = table_info['name']
    description = table_info['description']
    filename = table_info['filename']
    filepath = os.path.join(output_dir, filename)
    
    try:
        print(f"\n📊 Exporting: {table_name}")
        print(f"   Description: {description}")
        
        # Read the entire table from PostgreSQL into a DataFrame
        # This executes: SELECT * FROM table_name
        df = pd.read_sql_table(table_name, pg_engine)
        
        # Display table statistics
        print(f"   Rows: {len(df):,}")
        print(f"   Columns: {len(df.columns)}")
        
        # Export DataFrame to CSV file
        # index=False means don't include row numbers in CSV
        # encoding='utf-8' ensures special characters are preserved
        df.to_csv(filepath, index=False, encoding='utf-8')
        
        # Get file size in MB for reference
        file_size = os.path.getsize(filepath) / (1024 * 1024)  # Convert bytes to MB
        print(f"   ✓ Saved to: {filename} ({file_size:.2f} MB)")
        
        successful_exports += 1
        
    except Exception as e:
        # If export fails, print error but continue with other tables
        print(f"   ✗ Error exporting {table_name}: {e}")
        failed_exports += 1

# ============================================================================
# STEP 5: DISPLAY SUMMARY
# ============================================================================
print("\n" + "=" * 60)
print("EXPORT SUMMARY")
print("=" * 60)
print(f"Total tables: {total_tables}")
print(f"Successfully exported: {successful_exports}")
print(f"Failed: {failed_exports}")
print(f"\nAll CSV files saved in: {os.path.abspath(output_dir)}")

# ============================================================================
# STEP 6: CREATE README FILE FOR TEAM MEMBERS
# ============================================================================
# Generate a README file with instructions for team members
readme_path = os.path.join(output_dir, 'README.txt')
with open(readme_path, 'w', encoding='utf-8') as f:
    f.write("=" * 70 + "\n")
    f.write("POSTGRESQL DATABASE EXPORTS - TUTORIAL_DB\n")
    f.write("=" * 70 + "\n\n")
    f.write("This folder contains CSV exports from the tutorial_db PostgreSQL database.\n\n")
    
    f.write("FILES INCLUDED:\n")
    f.write("-" * 70 + "\n")
    for table_info in tables:
        f.write(f"• {table_info['filename']}\n")
        f.write(f"  Description: {table_info['description']}\n\n")
    
    f.write("\n" + "=" * 70 + "\n")
    f.write("HOW TO IMPORT INTO PGADMIN:\n")
    f.write("=" * 70 + "\n")
    f.write("1. Open pgAdmin and connect to your PostgreSQL server\n")
    f.write("2. Create a new database called 'tutorial_db' (if it doesn't exist)\n")
    f.write("3. Right-click on the database → Query Tool\n")
    f.write("4. Create tables using the schema below\n")
    f.write("5. Right-click on each table → Import/Export Data\n")
    f.write("6. Select the corresponding CSV file\n")
    f.write("7. Set format to CSV with header row enabled\n\n")
    
    f.write("=" * 70 + "\n")
    f.write("TABLE SCHEMAS (CREATE THESE FIRST):\n")
    f.write("=" * 70 + "\n\n")
    
    f.write("-- 1. Depression Index Table\n")
    f.write("CREATE TABLE depression_index (\n")
    f.write("    date DATE PRIMARY KEY,\n")
    f.write("    depression_index FLOAT\n")
    f.write(");\n\n")
    
    f.write("-- 2. News Articles Table\n")
    f.write("CREATE TABLE ccnews_depression (\n")
    f.write("    date VARCHAR(20),\n")
    f.write("    title TEXT,\n")
    f.write("    text TEXT\n")
    f.write(");\n\n")
    
    f.write("-- 3. Stock Data Table (Normalized)\n")
    f.write("CREATE TABLE stock_data (\n")
    f.write("    date VARCHAR(20),\n")
    f.write("    ticker VARCHAR(10),\n")
    f.write("    open FLOAT,\n")
    f.write("    high FLOAT,\n")
    f.write("    low FLOAT,\n")
    f.write("    close FLOAT,\n")
    f.write("    volume FLOAT\n")
    f.write(");\n\n")
    
    f.write("-- 4. S&P 500 Table\n")
    f.write("CREATE TABLE sp500 (\n")
    f.write("    date VARCHAR(20),\n")
    f.write("    close_gspc FLOAT,\n")
    f.write("    high_gspc FLOAT,\n")
    f.write("    low_gspc FLOAT,\n")
    f.write("    open_gspc FLOAT,\n")
    f.write("    volume_gspc FLOAT,\n")
    f.write("    return FLOAT,\n")
    f.write("    volatility_7 FLOAT\n")
    f.write(");\n\n")
    
    f.write("-- 5. Rainfall Table\n")
    f.write("CREATE TABLE rainfall (\n")
    f.write("    date VARCHAR(20),\n")
    f.write("    -- Add columns for each state (51 columns total)\n")
    f.write("    -- See the CSV header for complete column list\n")
    f.write(");\n\n")
    
    f.write("=" * 70 + "\n")
    f.write("ALTERNATIVE: QUICK IMPORT WITH PSQL COMMAND\n")
    f.write("=" * 70 + "\n")
    f.write("If you have psql command-line tool:\n\n")
    f.write("psql -U postgres -d tutorial_db -c \"\\COPY depression_index FROM 'depression_index.csv' CSV HEADER\"\n")
    f.write("psql -U postgres -d tutorial_db -c \"\\COPY ccnews_depression FROM 'ccnews_depression.csv' CSV HEADER\"\n")
    f.write("psql -U postgres -d tutorial_db -c \"\\COPY stock_data FROM 'stock_data.csv' CSV HEADER\"\n")
    f.write("psql -U postgres -d tutorial_db -c \"\\COPY sp500 FROM 'sp500.csv' CSV HEADER\"\n")
    f.write("psql -U postgres -d tutorial_db -c \"\\COPY rainfall FROM 'rainfall.csv' CSV HEADER\"\n\n")

print(f"\n📄 README file created: {readme_path}")
print("\n✅ Export complete! Share the '{output_dir}' folder with your team.")

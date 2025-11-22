import json
import os
from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
import pandas as pd
from typing import Dict, Any

app = FastAPI(title="Dataset Import API", description="API to import datasets into MongoDB")

# MongoDB connection
client = MongoClient('mongodb://localhost:37017/db')
db = client['db']

# Dataset configurations
DATASETS = {
    'sp500': 'sp500.csv',
    'depression_index': 'depression_index.csv',
    'rainfall': 'rainfall.csv',
    'ccnews_depression': 'ccnews_depression.csv',
    'stock_data': 'stock_data.csv'
}

DATASET_DIR = os.path.join(os.path.dirname(__file__), '..', 'dataset')

@app.get("/")
def read_root():
    return {"message": "Dataset Import API", "endpoints": ["/import-all", "/import/{dataset_name}"]}

@app.post("/import/{dataset_name}")
def import_dataset(dataset_name: str) -> Dict[str, Any]:
    if dataset_name not in DATASETS:
        raise HTTPException(status_code=404, detail=f"Dataset {dataset_name} not found")

    file_path = os.path.join(DATASET_DIR, DATASETS[dataset_name])

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"File {file_path} not found")

    try:
        # Read CSV
        df = pd.read_csv(file_path)

        # Convert to dict and insert
        collection = db[dataset_name]
        collection.drop()  # Clear existing data
        records = df.to_dict('records')
        result = collection.insert_many(records)

        return {
            "message": f"Successfully imported {len(records)} records into {dataset_name}",
            "inserted_ids": len(result.inserted_ids)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error importing {dataset_name}: {str(e)}")

@app.post("/import-all")
def import_all_datasets() -> Dict[str, Any]:
    results = {}
    for dataset_name in DATASETS.keys():
        try:
            result = import_dataset(dataset_name)
            results[dataset_name] = result
        except HTTPException as e:
            results[dataset_name] = {"error": e.detail}

    return {"results": results}

if __name__ == "__main__":
    # Run import directly
    try:
        result = import_all_datasets()
        print("Import completed successfully!")
        print(result)
        
        # Save summary to JSON file
        summary_file = os.path.join(os.path.dirname(__file__), 'import_summary.json')
        with open(summary_file, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"Import summary saved to {summary_file}")
        
    except Exception as e:
        print(f"Error during import: {e}")
        print("Make sure MongoDB is running on localhost:27017")
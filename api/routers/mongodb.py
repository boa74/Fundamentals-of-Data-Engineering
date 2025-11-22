from fastapi import APIRouter, HTTPException, Query
from pymongo import MongoClient
from typing import List, Dict, Any, Optional
import json
from bson import ObjectId

router = APIRouter()

# MongoDB connection
mongo_client = MongoClient('mongodb://localhost:37017/db')
mongo_db = mongo_client['db']

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)

@router.get("/collections")
async def get_collections() -> List[str]:
    """Get list of available collections in MongoDB"""
    try:
        collections = mongo_db.list_collection_names()
        return collections
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get collections: {str(e)}")

@router.get("/query/{collection}")
async def query_collection(
    collection: str,
    query: str = Query("{}", description="MongoDB query as JSON string"),
    limit: int = Query(10, description="Maximum number of documents to return", ge=1, le=1000)
) -> Dict[str, Any]:
    """Query a MongoDB collection"""
    try:
        # Parse query
        query_dict = json.loads(query) if query.strip() else {}

        # Get collection
        coll = mongo_db[collection]

        # Execute query
        cursor = coll.find(query_dict).limit(limit)
        results = list(cursor)

        # Convert ObjectId to string for JSON serialization
        for doc in results:
            if '_id' in doc:
                doc['_id'] = str(doc['_id'])

        return {
            "collection": collection,
            "query": query_dict,
            "limit": limit,
            "count": len(results),
            "results": results
        }

    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON query: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")

@router.get("/collection-info/{collection}")
async def get_collection_info(collection: str) -> Dict[str, Any]:
    """Get information about a collection"""
    try:
        coll = mongo_db[collection]
        count = coll.count_documents({})
        sample_doc = coll.find_one()

        if sample_doc and '_id' in sample_doc:
            sample_doc['_id'] = str(sample_doc['_id'])

        return {
            "collection": collection,
            "document_count": count,
            "sample_document": sample_doc
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get collection info: {str(e)}")
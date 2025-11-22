import requests
import json

BASE_URL = "http://127.0.0.1:8002"

def test_mongodb_collections():
    try:
        response = requests.get(f"{BASE_URL}/mongodb/collections")
        if response.status_code == 200:
            collections = response.json()
            print("MongoDB Collections:", collections)
            return collections
        else:
            print(f"Error getting collections: {response.status_code}")
            return []
    except Exception as e:
        print(f"Error: {e}")
        return []

def test_mongodb_query(collection):
    try:
        response = requests.get(f"{BASE_URL}/mongodb/query/{collection}?limit=5")
        if response.status_code == 200:
            data = response.json()
            print(f"MongoDB Query Results for {collection}:")
            print(json.dumps(data, indent=2))
        else:
            print(f"Error querying {collection}: {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")

def test_postgresql_tables():
    try:
        response = requests.get(f"{BASE_URL}/postgresql/tables")
        if response.status_code == 200:
            tables = response.json()
            print("PostgreSQL Tables:", tables)
            return tables
        else:
            print(f"Error getting tables: {response.status_code}")
            return []
    except Exception as e:
        print(f"Error: {e}")
        return []

def test_postgresql_query():
    try:
        query = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' LIMIT 5"
        response = requests.post(f"{BASE_URL}/postgresql/query", params={"query": query})
        if response.status_code == 200:
            data = response.json()
            print("PostgreSQL Query Results:")
            print(json.dumps(data, indent=2))
        else:
            print(f"Error executing query: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("Testing FastAPI endpoints...")

    # Test MongoDB
    collections = test_mongodb_collections()
    if collections:
        test_mongodb_query(collections[0])

    # Test PostgreSQL
    tables = test_postgresql_tables()
    test_postgresql_query()
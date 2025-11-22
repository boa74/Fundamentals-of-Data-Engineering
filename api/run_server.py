#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import uvicorn
import threading
import time
import requests
import json

def start_server():
    """Start the FastAPI server"""
    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=8002,
        log_level='info',
        access_log=False  # Reduce log noise
    )

def test_endpoints():
    """Test all API endpoints"""
    time.sleep(2)  # Wait for server to start

    print("🚀 Testing FastAPI Data Engineering API")
    print("=" * 50)

    # Test root endpoint
    try:
        response = requests.get('http://127.0.0.1:8002/')
        if response.status_code == 200:
            data = response.json()
            print("✅ Root endpoint working")
            print(f"   Message: {data['message']}")
            print(f"   Version: {data['version']}")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Root endpoint error: {e}")

    # Test MongoDB collections
    try:
        response = requests.get('http://127.0.0.1:8002/mongodb/collections')
        if response.status_code == 200:
            collections = response.json()
            print(f"✅ MongoDB collections: {collections}")
        else:
            print(f"❌ MongoDB collections failed: {response.status_code}")
    except Exception as e:
        print(f"❌ MongoDB collections error: {e}")

    # Test MongoDB query
    try:
        response = requests.get('http://127.0.0.1:8002/mongodb/query/sp500?limit=2')
        if response.status_code == 200:
            data = response.json()
            print(f"✅ MongoDB query successful")
            print(f"   Collection: {data['collection']}")
            print(f"   Results count: {data['count']}")
            if data['results']:
                print(f"   Sample data keys: {list(data['results'][0].keys())[:5]}")
        else:
            print(f"❌ MongoDB query failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ MongoDB query error: {e}")

    # Test PostgreSQL tables
    try:
        response = requests.get('http://127.0.0.1:8002/postgresql/tables')
        if response.status_code == 200:
            tables = response.json()
            print(f"✅ PostgreSQL tables: {tables}")
        else:
            print(f"❌ PostgreSQL tables failed: {response.status_code}")
    except Exception as e:
        print(f"❌ PostgreSQL tables error: {e}")

    # Test PostgreSQL query
    try:
        query = "SELECT version()"
        response = requests.post('http://127.0.0.1:8002/postgresql/query', params={'query': query})
        if response.status_code == 200:
            data = response.json()
            print(f"✅ PostgreSQL query successful")
            print(f"   Query: {data['query'][:50]}...")
            print(f"   Results count: {data['row_count']}")
        else:
            print(f"❌ PostgreSQL query failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ PostgreSQL query error: {e}")

    print("\n" + "=" * 50)
    print("🎉 API testing completed!")
    print("📖 API Documentation: http://127.0.0.1:8002/docs")

if __name__ == "__main__":
    # Start server in background thread
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()

    # Test the endpoints
    test_endpoints()

    # Keep the main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 Shutting down server...")
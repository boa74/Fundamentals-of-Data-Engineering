#!/usr/bin/env python3

import sys
import os
sys.path.append('/Users/nsls/Documents/Github/Fundamentals-of-Data-Engineering/api')

try:
    from routers.mongodb import mongo_client, mongo_db
    print("✓ MongoDB connection imported successfully")
    collections = mongo_db.list_collection_names()
    print(f"✓ MongoDB collections: {collections}")
except Exception as e:
    print(f"✗ MongoDB connection failed: {e}")

try:
    from routers.postgresql import get_postgres_connection
    print("✓ PostgreSQL connection function imported successfully")
    conn = get_postgres_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT version()")
    version = cursor.fetchone()
    print(f"✓ PostgreSQL connected: {version[0][:50]}...")
    cursor.close()
    conn.close()
except Exception as e:
    print(f"✗ PostgreSQL connection failed: {e}")

try:
    from main import app
    print("✓ Main app imported successfully")
    print(f"✓ App routes: {len(app.routes)}")
except Exception as e:
    print(f"✗ Main app import failed: {e}")
from fastapi import APIRouter, HTTPException, Query
from psycopg2 import connect
from psycopg2.extras import RealDictCursor
from typing import List, Dict, Any, Optional
import re

router = APIRouter()

def get_postgres_connection():
    """Get PostgreSQL database connection"""
    return connect(
        host="localhost",
        port=45432,
        database="db",
        user="admin",
        password="PassW0rd"
    )

@router.get("/tables")
async def get_tables() -> List[str]:
    """Get list of available tables in PostgreSQL"""
    try:
        conn = get_postgres_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)

        tables = [row[0] for row in cursor.fetchall()]
        cursor.close()
        conn.close()

        return tables
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get tables: {str(e)}")

@router.post("/query")
async def execute_query(
    query: str = Query(..., description="SQL query to execute"),
    limit: int = Query(100, description="Maximum number of rows to return", ge=1, le=10000)
) -> Dict[str, Any]:
    """Execute a SQL query (SELECT only for security)"""
    try:
        # Security check - only allow SELECT queries
        query_upper = query.strip().upper()
        if not query_upper.startswith('SELECT'):
            raise HTTPException(
                status_code=400,
                detail="Only SELECT queries are allowed for security reasons"
            )

        # Additional safety checks
        dangerous_keywords = ['DROP', 'DELETE', 'INSERT', 'UPDATE', 'ALTER', 'CREATE', 'TRUNCATE']
        for keyword in dangerous_keywords:
            if re.search(r'\b' + keyword + r'\b', query_upper):
                raise HTTPException(
                    status_code=400,
                    detail=f"Query contains forbidden keyword: {keyword}"
                )

        conn = get_postgres_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Add LIMIT if not present
        if 'LIMIT' not in query_upper:
            query += f" LIMIT {limit}"

        cursor.execute(query)
        results = cursor.fetchall()

        # Get column names
        columns = list(results[0].keys()) if results else []

        cursor.close()
        conn.close()

        return {
            "query": query,
            "columns": columns,
            "row_count": len(results),
            "results": [dict(row) for row in results]
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query execution failed: {str(e)}")

@router.get("/table-info/{table}")
async def get_table_info(table: str) -> Dict[str, Any]:
    """Get information about a table"""
    try:
        conn = get_postgres_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Get column information
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = %s AND table_schema = 'public'
            ORDER BY ordinal_position
        """, (table,))

        columns = cursor.fetchall()

        # Get row count
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        row_count = cursor.fetchone()['count']

        # Get sample data
        cursor.execute(f"SELECT * FROM {table} LIMIT 5")
        sample_data = cursor.fetchall()

        cursor.close()
        conn.close()

        return {
            "table": table,
            "row_count": row_count,
            "columns": [dict(col) for col in columns],
            "sample_data": [dict(row) for row in sample_data]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get table info: {str(e)}")
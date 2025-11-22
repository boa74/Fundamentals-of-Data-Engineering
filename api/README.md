# Data Engineering API

A FastAPI-based REST API for querying MongoDB and PostgreSQL databases containing financial and economic datasets.

## Features

- **MongoDB Integration**: Query collections with JSON-based queries
- **PostgreSQL Integration**: Execute SQL SELECT queries safely
- **Interactive Documentation**: Built-in Swagger UI at `/docs`
- **CORS Support**: Cross-origin requests enabled
- **Security**: PostgreSQL queries limited to SELECT statements only

## Datasets

### MongoDB Collections
- `sp500`: S&P 500 historical price data
- `depression_index`: Economic depression indicators
- `rainfall`: Weather/rainfall data
- `ccnews_depression`: News articles related to depression

### PostgreSQL Tables
Currently empty - can be populated with relational data as needed.

## API Endpoints

### MongoDB Endpoints

#### GET `/mongodb/collections`
Get list of available collections.

**Response:**
```json
["sp500", "depression_index", "rainfall", "ccnews_depression"]
```

#### GET `/mongodb/query/{collection}`
Query a specific collection.

**Parameters:**
- `query` (string): MongoDB query as JSON string (default: "{}")
- `limit` (int): Maximum results to return (default: 10, max: 1000)

**Example:**
```
GET /mongodb/query/sp500?limit=5
```

#### GET `/mongodb/collection-info/{collection}`
Get information about a collection including document count and sample data.

### PostgreSQL Endpoints

#### GET `/postgresql/tables`
Get list of available tables.

#### POST `/postgresql/query`
Execute a SQL SELECT query.

**Parameters:**
- `query` (string): SQL query to execute (must be SELECT)
- `limit` (int): Maximum rows to return (default: 100, max: 10000)

**Example:**
```
POST /postgresql/query?query=SELECT%20*%20FROM%20users%20LIMIT%205
```

#### GET `/postgresql/table-info/{table}`
Get information about a table including column details and sample data.

## Running the API

1. Ensure Docker containers are running:
```bash
docker-compose up -d apan5400-mongodb apan5400-postgres
```

2. Install dependencies:
```bash
cd api
pip install -r requirements.txt
```

3. Run the server:
```bash
python run_server.py
```

The API will be available at `http://127.0.0.1:8002`

## Testing

Run the included test script:
```bash
python run_server.py
```

This will start the server and automatically test all endpoints.

## Security Notes

- PostgreSQL queries are restricted to SELECT statements only
- Dangerous keywords (DROP, DELETE, INSERT, UPDATE, etc.) are blocked
- MongoDB queries support full JSON query syntax
- CORS is enabled for cross-origin requests

## Development

- Built with FastAPI for high performance
- Automatic API documentation generation
- Modular router-based architecture
- Comprehensive error handling
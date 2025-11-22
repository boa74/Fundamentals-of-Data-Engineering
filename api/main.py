from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import mongodb, postgresql

app = FastAPI(
    title="Data Engineering API",
    description="API for querying MongoDB and PostgreSQL databases",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    mongodb.router,
    prefix="/mongodb",
    tags=["MongoDB"]
)

app.include_router(
    postgresql.router,
    prefix="/postgresql",
    tags=["PostgreSQL"]
)

@app.get("/")
def read_root():
    return {
        "message": "Data Engineering API",
        "version": "1.0.0",
        "endpoints": {
            "mongodb": "/mongodb",
            "postgresql": "/postgresql"
        }
    }

# services/analytics-service/main.py
from fastapi import FastAPI, HTTPException, status, Depends
from pydantic import BaseModel, Field
from typing import Any, List, Dict
from datetime import datetime
import motor.motor_asyncio # Async MongoDB driver
import os
from contextlib import asynccontextmanager

# --- Configuration ---
# Use environment variables for sensitive info
MONGO_DETAILS = os.getenv("MONGO_DETAILS", "mongodb://localhost:27017") # Default for local Docker setup
# In Docker Compose, use service name: "mongodb://mongo_db:27017"
# In real deployments, use proper connection strings with auth

# Global variable for MongoDB client and database (managed by lifespan)
mongo_client = None
db = None

# --- Lifespan Management for DB Connection ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Connect to MongoDB
    global mongo_client, db
    print(f"Connecting to MongoDB at {MONGO_DETAILS}...")
    try:
        mongo_client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)
        # Ping server to verify connection early
        await mongo_client.admin.command('ping')
        db = mongo_client.analytics_db # Use a specific database name
        print("Successfully connected to MongoDB.")
    except Exception as e:
         print(f"Error connecting to MongoDB: {e}")
         # Decide if the app should fail to start or run without DB
         # For this service, DB is critical, so maybe raise the exception
         # raise RuntimeError(f"Could not connect to MongoDB: {e}") from e
         mongo_client = None # Ensure client is None if connection failed
         db = None

    yield # Application runs here

    # Shutdown: Disconnect from MongoDB
    if mongo_client:
        print("Closing MongoDB connection.")
        mongo_client.close()


app = FastAPI(
    title="Analytics Service",
    description="Receives event logs and provides analytics data.",
    version="0.1.0",
    lifespan=lifespan # Register the lifespan context manager
)

# --- Database Dependency ---
# Simple dependency to check if DB connection is available
async def get_database():
    if db is None:
        raise HTTPException(status_code=503, detail="Database connection not available")
    return db

# --- Pydantic Models ---
class EventLog(BaseModel):
    event_type: str = Field(..., index=True) # e.g., "task_created", "user_login", "task_completed"
    user_id: str | None = Field(None, index=True)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    details: Dict[str, Any] | None = None # Flexible dictionary for event-specific data

# --- API Endpoints ---
@app.post("/log-event", status_code=status.HTTP_202_ACCEPTED)
async def log_event(
    event: EventLog,
    database = Depends(get_database) # Inject DB dependency
):
    """Receives an event and logs it to MongoDB."""
    try:
        # Collection name could be dynamic (e.g., based on year/month) or static
        collection = database.event_logs
        result = await collection.insert_one(event.model_dump())
        # Return confirmation or the ID of the inserted document
        return {"message": "Event logged successfully", "id": str(result.inserted_id)}
    except Exception as e:
         print(f"Error logging event to MongoDB: {e}")
         # Decide on error handling: retry? dead-letter queue? just log?
         # For now, raise an internal server error
         raise HTTPException(status_code=500, detail="Failed to log event")


@app.get("/stats/task-completion", response_model=Dict[str, Any])
async def get_task_completion_stats(database = Depends(get_database)):
    """Example endpoint to calculate some simple stats."""
    # --- !!! Placeholder - Requires Aggregation Query !!! ---
    # This is where you'd write a MongoDB aggregation pipeline
    # Example: Count tasks completed per day/week/user etc.
    print("Calculating task completion stats (placeholder)...")

    # Example: Count total events logged
    try:
        collection = database.event_logs
        total_events = await collection.count_documents({})
        completed_tasks_count = await collection.count_documents({"event_type": "task_completed"})

        # Add more complex aggregation pipelines here later
        # pipeline = [ { '$match': { 'event_type': 'task_completed' } }, ... ]
        # results = await collection.aggregate(pipeline).to_list(length=None)

        return {
            "total_events_logged": total_events,
            "completed_tasks_count": completed_tasks_count,
            "detail": "More detailed stats require implementing aggregation queries."
        }
    except Exception as e:
        print(f"Error retrieving stats from MongoDB: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve statistics")

@app.get("/health")
async def health_check(database = Depends(get_database)):
    """Basic health check including DB connection."""
    # The Depends(get_database) already checks DB availability
    return {"status": "ok", "database_status": "connected"}
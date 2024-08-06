from os import getenv
from dotenv import load_dotenv
from fastapi import FastAPI
from services.alloyDB import init_db_pool
from services.in_memory_cache import set_expiration_time, start_cleaning_task
from controllers.extractTyc import initialize_pubsub_service
app = FastAPI()

# Load environment variables
load_dotenv()
cleaning_interval_hours = int(getenv("CLEANING_INTERVAL_HOURS", 1))  # Default to 1 hour

async def startup_event():
    await init_db_pool()
    print("db pool initialized succesfully")
     # Initialize in-memory cache
    set_expiration_time(cleaning_interval_hours)
    start_cleaning_task()
    print("In-memory cache initialized successfully")
    await initialize_pubsub_service()
    print("pull subscriber initialized succesfully")

    return

app.add_event_handler("startup", startup_event)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)


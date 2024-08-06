import time
import asyncio
from typing import Dict, Any, NoReturn

# Global variables
cache: Dict[str, Dict[str, Any]] = {}
expiration_time: int = 7 * 60 * 60  # 1 hour in seconds (default)

async def add_message(message_hash: str) -> None:
    cache[message_hash] = {"timestamp": time.time()}

async def is_message_processed(message_hash: str) -> bool:
    return message_hash in cache

async def clean_old_messages() -> None:
    global cache
    current_time = time.time()
    cache = {
        k: v for k, v in cache.items()
        if current_time - v["timestamp"] < expiration_time
    }

async def clean_old_messages_periodically() -> NoReturn:
    while True:
        await clean_old_messages()
        await asyncio.sleep(expiration_time)

def set_expiration_time(days: int)  -> None:
    global expiration_time
    expiration_time = days * 24 * 60 * 60

# Initialize the cleaning task
cleaning_task = None

def start_cleaning_task() -> None:
    global cleaning_task
    cleaning_task = asyncio.create_task(clean_old_messages_periodically())

def stop_cleaning_task() -> None:
    global cleaning_task
    if cleaning_task:
        cleaning_task.cancel()
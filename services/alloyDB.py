import asyncpg
import logging
from os import getenv
from dotenv import load_dotenv
from fastapi import HTTPException

# Load environment variables from a .env file
load_dotenv()

# Configure logging to output detailed logs
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Database connection pool (shared resource)
pool = None


# Initialize the asyncpg connection pool
async def init_db_pool():
    """
    Initialize the database connection pool.

    Parameters:
    - None

    Returns:
    - None
    """
    global pool
    pool = await asyncpg.create_pool(
        user=getenv("DB_USER"),  # Database user
        password=getenv("DB_PASSWORD"),  # Database password
        host=getenv("DB_HOST"),  # Database host address
        port=getenv("DB_PORT"),  # Port number to connect
        database=getenv("DB_NAME"),  # Name of the target database
    )


# Execute a single SQL query and handle exceptions
async def execute_query(query: str, params: list = None, fetch: bool = False):
    """
    Execute a SQL query which can be a data manipulation or data retrieval type.

    Parameters:
    - query (str): The SQL query string to execute.
    - params (list, optional): Parameters to pass to the SQL query. Defaults to None.
    - fetch (bool): Flag to determine if the query expects a return value (e.g., SELECT).

    Returns:
    - List of dict or dict or None: The result of the query based on the fetch flag.

    Raises:
    - HTTPException: If any database or execution error occurs.
    """
    try:
        async with pool.acquire() as conn:  # Assume `pool` is previously defined
            async with conn.transaction():
                if fetch:
                    # Use fetch for SELECT queries or any query that returns data
                    result = (
                        await conn.fetch(query, *params)
                        if params
                        else await conn.fetch(query)
                    )
                    # Convert each Record to dict with keys
                    return [dict(record) for record in result] if result else []
                else:
                    # Use execute for INSERT, UPDATE, DELETE, etc., that do not need to return data
                    (
                        await conn.execute(query, *params)
                        if params
                        else await conn.execute(query)
                    )
                    return None
    except asyncpg.exceptions.PostgresError as e:
        logging.error(f"Database operation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logging.error(f"Database operation failed: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


# Execute a bulk query (multiple statements) and handle exceptions
async def execute_bulk_query(query: str, data: list) -> int:
    """
    Execute a bulk SQL query with multiple data entries.

    Parameters:
    - query (str): The SQL query string to execute (with placeholders).
    - data (list): A list of tuples containing data to fill the query placeholders.

    Returns:
    - int: The number of rows affected by the query.

    Raises:
    - Exception: If any database or execution error occurs.
    """
    try:
        logging.info(f"Executing bulk query with {len(data)} records")
        logging.debug(f"Query: {query}")
        logging.debug(f"Data: {data}")
        
        # Acquire a database connection and start a transaction
        async with pool.acquire() as conn:
            async with conn.transaction():
                # Execute multiple statements with provided data
                result = await conn.executemany(query, data)
            logging.info(f"Bulk query executed successfully. Rows affected: {result}")
            return result
    except asyncpg.exceptions.PostgresError as e:
        # Handle specific PostgreSQL errors
        logging.error(f"PostgreSQL error in bulk query execution: {e}")
        raise Exception(f"PostgreSQL error: {str(e)}")
    except Exception as e:
        # Handle any general exception during query execution
        logging.error(f"Unexpected error in bulk query execution: {e}")
        raise Exception(f"Unexpected error: {str(e)}")
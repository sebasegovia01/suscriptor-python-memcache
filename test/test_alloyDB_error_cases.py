import pytest
import asyncpg
from unittest.mock import AsyncMock
from fastapi import HTTPException
from services.alloyDB import execute_query, execute_bulk_query

@pytest.mark.asyncio
async def test_general_exception_handling_in_execute_query(mocker):
    mock_acquire = mocker.patch('asyncpg.pool.Pool.acquire', new_callable=AsyncMock)
    mock_acquire.side_effect = Exception("Unexpected error")
    with pytest.raises(HTTPException) as exc_info:
        await execute_query("SELECT * FROM users", fetch=True)
    assert "An unexpected error occurred" in str(exc_info.value.detail)

@pytest.mark.asyncio
async def test_execute_query_no_fetch_no_params(db_mocks):
    await db_mocks
    query = "UPDATE users SET name = 'Alice' WHERE id = 1"
    result = await execute_query(query, fetch=False)
    assert result is None


@pytest.mark.asyncio
async def test_general_exception_handling_in_execute_bulk_query(bulk_db_mocks):
    pool = await bulk_db_mocks
    mock_acquire = pool.acquire
    mock_acquire.side_effect = Exception("Unexpected error")
    query = "INSERT INTO users (name, age) VALUES ($1, $2)"
    data = [("Alice", 30)]

    with pytest.raises(HTTPException) as exc_info:
        await execute_bulk_query(query, data)
    
    assert exc_info.value.status_code == 500
    assert "Bulk query execution failed" in str(exc_info.value.detail)

@pytest.mark.asyncio
async def test_execute_bulk_query_postgres_error(bulk_db_mocks):
    pool = await bulk_db_mocks
    query = "INSERT INTO my_table (col1, col2) VALUES ($1, $2)"
    data = [(1, 'data1'), (2, 'data2')]
    mock_conn = pool.acquire.return_value.__aenter__.return_value
    mock_conn.executemany.side_effect = asyncpg.exceptions.PostgresError("Database error")

    with pytest.raises(HTTPException) as excinfo:
        await execute_bulk_query(query, data)
    
    mock_conn.executemany.assert_called_once_with(query, data)
    assert excinfo.value.status_code == 500
    assert "Database error" in str(excinfo.value.detail)

@pytest.mark.asyncio
async def test_execute_bulk_query_general_exception(bulk_db_mocks):
    pool = await bulk_db_mocks
    query = "INSERT INTO my_table (col1, col2) VALUES ($1, $2)"
    data = [(1, 'data1'), (2, 'data2')]
    mock_conn = pool.acquire.return_value.__aenter__.return_value
    mock_conn.executemany.side_effect = Exception("General error")

    with pytest.raises(HTTPException) as excinfo:
        await execute_bulk_query(query, data)
    
    mock_conn.executemany.assert_called_once_with(query, data)
    assert excinfo.value.status_code == 500
    assert "Bulk query execution failed" in str(excinfo.value.detail)


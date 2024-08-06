import pytest
from unittest.mock import AsyncMock
from services.alloyDB import execute_query, execute_bulk_query, init_db_pool

@pytest.mark.asyncio
async def test_execute_query(db_mocks):
    await db_mocks
    query = "SELECT * FROM users"
    result = await execute_query(query, fetch=True)
    assert result == [{"mocked_key": "mocked_value"}]

@pytest.mark.asyncio
async def test_execute_bulk_query_success(bulk_db_mocks):
    pool = await bulk_db_mocks
    query = "INSERT INTO my_table (col1, col2) VALUES ($1, $2)"
    data = [(1, 'data1'), (2, 'data2')]
    mock_conn = pool.acquire.return_value.__aenter__.return_value
    mock_conn.executemany.return_value = "Success"

    result = await execute_bulk_query(query, data)
    
    mock_conn.executemany.assert_called_once_with(query, data)
    assert result == "Success"

@pytest.mark.asyncio
async def test_pool_initialization(mocker):
    from services import alloyDB
    assert alloyDB.pool is None
    mock_create_pool = mocker.patch('asyncpg.create_pool', new_callable=AsyncMock)
    await init_db_pool()
    assert alloyDB.pool is not None
    mock_create_pool.assert_called_once()


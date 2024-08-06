import pytest
from unittest import mock
from fastapi import HTTPException
from services.redis import check_redis_connection

@pytest.mark.asyncio
async def test_check_redis_connection_success(mock_redis_client):
    mock_redis_client.ping.return_value = None
    with mock.patch('logging.info') as mock_log_info:
        await check_redis_connection()
        mock_redis_client.ping.assert_called_once()
        mock_log_info.assert_called_once_with("Redis connection successfull.")


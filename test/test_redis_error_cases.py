import pytest
from unittest import mock
from fastapi import HTTPException
from services.redis import check_redis_connection

@pytest.mark.asyncio
async def test_check_redis_connection_failure(mock_redis_client):
    mock_redis_client.ping.side_effect = Exception("Redis connection error")

    with mock.patch('logging.error') as mock_log_error:
        with pytest.raises(HTTPException) as exc_info:
            await check_redis_connection()

        assert exc_info.value.status_code == 500
        assert exc_info.value.detail == "Redis connection check failed"
        mock_redis_client.ping.assert_called_once()
        mock_log_error.assert_called_once_with("Redis connection check failed", exc_info=True)


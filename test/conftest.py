from unittest import mock
from unittest.mock import AsyncMock, MagicMock, Mock, patch
import asyncpg
import pytest, os, sys
import pytest_asyncio

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Global env configs
def pytest_configure():
    os.environ["REDIS_URL"] = "redis://localhost:6379"
    os.environ["DB_USER"] = "test_user"
    os.environ["DB_PASSWORD"] = "test_pass"
    os.environ["DB_HOST"] = "localhost"
    os.environ["DB_PORT"] = "5432"
    os.environ["DB_NAME"] = "test_db"
# -------Alloydb Mocks-------
@pytest.fixture
async def db_mocks(mocker):
    mock_conn = AsyncMock(spec=asyncpg.Connection)
    mock_conn.transaction.return_value.__aenter__.return_value = mock_conn
    mock_conn.transaction.return_value.__aexit__.return_value = None
    mock_conn.fetch = AsyncMock(return_value=[{"mocked_key": "mocked_value"}])
    mock_conn.execute = AsyncMock(return_value="Mocked result")
    mock_conn.executemany = AsyncMock(return_value="Mocked result")
    mock_pool = AsyncMock(spec=asyncpg.pool.Pool)
    mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
    mock_pool.acquire.return_value.__aexit__.return_value = None
    mocker.patch('services.alloyDB.pool', mock_pool)
    
    return mock_conn

@pytest.fixture
async def bulk_db_mocks(mocker):
    mock_pool = mocker.patch('services.alloyDB.pool', new_callable=AsyncMock)
    mock_conn = AsyncMock(spec=asyncpg.Connection)
    mock_transaction = AsyncMock()
    mock_transaction.__aenter__.return_value = mock_transaction
    mock_transaction.__aexit__.return_value = None
    mock_conn.transaction.return_value = mock_transaction
    mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
    mock_pool.acquire.return_value.__aexit__.return_value = None

    return mock_pool
# -------Redis Mocks-------
@pytest.fixture
def mock_redis_client():
    with mock.patch("services.redis.redis_client") as mock_client:
        yield mock_client
with mock.patch(
    "google.oauth2.service_account.Credentials.from_service_account_file"
) as mock_creds:
    mock_creds_instance = mock.Mock()
    mock_creds.return_value = mock_creds_instance
    with mock.patch("google.cloud.storage.Client") as mock_client:
        mock_instance = mock_client.return_value
        import services.storage as storage_module

@pytest.fixture
def mock_storage_client():
    with mock.patch("google.cloud.storage.Client") as mock_client:
        mock_instance = mock_client.return_value
        yield mock_instance

@pytest.fixture
def mock_service_account():
    with mock.patch(
        "google.oauth2.service_account.Credentials.from_service_account_file"
    ) as mock_creds:
        mock_creds_instance = mock_creds.return_value
        yield mock_creds_instance

@pytest.fixture
def mock_bucket():
    with mock.patch.object(
        storage_module, "bucket", new_callable=mock.Mock
    ) as mock_bucket:
        yield mock_bucket


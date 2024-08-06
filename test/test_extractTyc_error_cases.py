import sys, pytest, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from fastapi.testclient import TestClient
from fastapi import FastAPI
from controllers.extractTyc import initialize_pubsub_service
from api.router import router
app = FastAPI()
app.include_router(router)
# Testing a request that should return 422
client = TestClient(app)
@pytest.mark.asyncio
async def test_invalid_request_422(mock_redis_client, bulk_db_mocks):
    response = client.post("/api/v1/extractTyc", json={"invalidField": "invalidValue"})
    assert response.status_code == 422
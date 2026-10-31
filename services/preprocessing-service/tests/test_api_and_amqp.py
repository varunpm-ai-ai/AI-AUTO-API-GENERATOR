"""
Tests for HTTP API Endpoints.
"""
import pytest
from httpx import AsyncClient, ASGITransport
from main import app


@pytest.mark.asyncio
async def test_health_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "UP"
    assert data["service"] == "preprocessing-service"


@pytest.mark.asyncio
async def test_ready_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "READY"


@pytest.mark.asyncio
async def test_preprocess_api_endpoint(sample_json_path):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        payload = {
            "job_id": "api-test-job-300",
            "dataset_id": "api-test-ds-300",
            "source_uri": f"file://{sample_json_path.resolve()}",
            "format_hint": "json"
        }
        response = await ac.post("/api/v1/preprocess", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "COMPLETED"
    assert data["row_count"] == 3
    assert data["processed_uri"] is not None

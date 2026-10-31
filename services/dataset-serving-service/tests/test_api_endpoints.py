"""
Integration Tests for Dataset Serving HTTP Endpoints.
Covers Search, Status, Metadata, Schema, Versions, Querying (GET/POST), and Download.
"""
import pytest
from httpx import AsyncClient, ASGITransport
from main import app


@pytest.mark.asyncio
async def test_health_and_ready():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        health_res = await ac.get("/health")
        assert health_res.status_code == 200
        assert health_res.json()["status"] == "UP"

        ready_res = await ac.get("/ready")
        assert ready_res.status_code == 200
        assert ready_res.json()["status"] == "READY"


@pytest.mark.asyncio
async def test_dataset_search(setup_test_dataset):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get(f"/api/v1/datasets/search?q={setup_test_dataset}")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "success"
        assert len(data["data"]) >= 1
        assert data["data"][0]["dataset_id"] == setup_test_dataset


@pytest.mark.asyncio
async def test_dataset_metadata(setup_test_dataset):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get(f"/api/v1/datasets/{setup_test_dataset}/metadata")
        assert res.status_code == 200
        data = res.json()["data"]
        assert data["dataset_id"] == setup_test_dataset
        assert data["row_count"] == 5
        assert data["column_count"] == 5


@pytest.mark.asyncio
async def test_dataset_schema(setup_test_dataset):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get(f"/api/v1/datasets/{setup_test_dataset}/schema")
        assert res.status_code == 200
        data = res.json()["data"]
        assert data["dataset_id"] == setup_test_dataset
        col_names = [col["name"] for col in data["columns"]]
        assert "id" in col_names
        assert "name" in col_names
        assert "salary" in col_names


@pytest.mark.asyncio
async def test_dataset_versions(setup_test_dataset):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get(f"/api/v1/datasets/{setup_test_dataset}/versions")
        assert res.status_code == 200
        data = res.json()["data"]
        assert data["total_versions"] >= 1


@pytest.mark.asyncio
async def test_dataset_status(setup_test_dataset):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get(f"/api/v1/datasets/{setup_test_dataset}/status")
        assert res.status_code == 200
        data = res.json()["data"]
        assert data["is_ready_for_serving"] is True
        assert data["status"] == "SERVING"


@pytest.mark.asyncio
async def test_dataset_query_get(setup_test_dataset):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # GET with projection and pagination
        res = await ac.get(f"/api/v1/datasets/{setup_test_dataset}/query?columns=id,name&page=1&page_size=2")
        assert res.status_code == 200
        body = res.json()
        assert len(body["data"]) == 2
        assert list(body["data"][0].keys()) == ["id", "name"]
        assert body["pagination"]["page"] == 1
        assert body["pagination"]["total_rows"] == 5
        assert body["pagination"]["has_next"] is True


@pytest.mark.asyncio
async def test_dataset_query_post(setup_test_dataset):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        payload = {
            "columns": ["id", "name", "department"],
            "filters": [
                {"column": "department", "operator": "eq", "value": "Engineering"}
            ],
            "sort": [{"column": "id", "direction": "desc"}],
            "page": 1,
            "page_size": 10
        }
        res = await ac.post(f"/api/v1/datasets/{setup_test_dataset}/query", json=payload)
        assert res.status_code == 200
        body = res.json()
        # Alice (id=1) and Charlie (id=3) are in Engineering
        assert len(body["data"]) == 2
        assert body["data"][0]["id"] == 3  # DESC sort puts Charlie first
        assert body["data"][1]["id"] == 1


@pytest.mark.asyncio
async def test_dataset_download_streaming(setup_test_dataset):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get(f"/api/v1/datasets/{setup_test_dataset}/download?format=csv")
        assert res.status_code == 200
        assert "text/csv" in res.headers["content-type"]
        assert b"Alice" in res.content
        assert b"Charlie" in res.content

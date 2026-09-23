import pytest


@pytest.mark.asyncio
async def test_health_and_readiness_endpoints(client):
    resp = await client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "UP"
    assert data["service"] == "dataset-catalog-service"

    resp2 = await client.get("/readiness")
    assert resp2.status_code == 200
    data2 = resp2.json()
    assert data2["status"] == "READY"


@pytest.mark.asyncio
async def test_register_and_get_dataset_api(client):
    register_payload = {
        "name": "e_commerce_orders",
        "description": "Online store purchase transactions",
        "domain": "e_commerce",
        "source": "shopify",
        "checksum": "e_comm_hash_111222333",
        "storage_ref": "s3://store-data/orders_2026.json",
        "storage_type": "object_storage",
        "file_size": 409600,
        "metadata": {"currency": "USD", "format": "json"}
    }

    # 1. Register Dataset API
    response = await client.post("/api/v1/catalog/datasets", json=register_payload)
    assert response.status_code == 201
    body = response.json()
    assert body["success"] is True
    dataset_data = body["data"]
    dataset_id = dataset_data["dataset_id"]
    assert dataset_data["name"] == "e_commerce_orders"
    assert len(dataset_data["versions"]) == 1
    version_id = dataset_data["versions"][0]["version_id"]

    # 2. List Datasets API
    list_resp = await client.get("/api/v1/catalog/datasets?domain=e_commerce")
    assert list_resp.status_code == 200
    list_body = list_resp.json()
    assert list_body["success"] is True
    assert list_body["data"]["total"] == 1
    assert list_body["data"]["items"][0]["dataset_id"] == dataset_id

    # 3. Get Dataset Detail API
    detail_resp = await client.get(f"/api/v1/catalog/datasets/{dataset_id}")
    assert detail_resp.status_code == 200
    detail_body = detail_resp.json()
    assert detail_body["data"]["dataset_id"] == dataset_id

    # 4. Get Version Detail API
    ver_resp = await client.get(f"/api/v1/catalog/datasets/{dataset_id}/versions/{version_id}")
    assert ver_resp.status_code == 200
    ver_body = ver_resp.json()
    assert ver_body["data"]["version_id"] == version_id
    assert ver_body["data"]["checksum"] == "e_comm_hash_111222333"

    # 5. Get Version Status API
    status_resp = await client.get(f"/api/v1/catalog/datasets/{dataset_id}/versions/{version_id}/status")
    assert status_resp.status_code == 200
    status_body = status_resp.json()
    assert status_body["data"]["version_id"] == version_id
    assert status_body["data"]["current_status"] == "RAW_REGISTERED"

    # 6. Resolve Identity API
    resolve_resp = await client.post(
        "/api/v1/catalog/resolve-identity",
        json={"name": "e_commerce_orders", "source": "shopify", "domain": "e_commerce"}
    )
    assert resolve_resp.status_code == 200
    resolve_body = resolve_resp.json()
    assert resolve_body["data"]["is_existing"] is True
    assert resolve_body["data"]["dataset_id"] == dataset_id

    # 7. Check Duplicate API
    dup_resp = await client.post(
        "/api/v1/catalog/check-duplicate",
        json={"checksum": "e_comm_hash_111222333", "storage_ref": "s3://store-data/orders_2026.json"}
    )
    assert dup_resp.status_code == 200
    dup_body = dup_resp.json()
    assert dup_body["data"]["is_duplicate"] is True

    # 8. Preprocessing Result Callback API
    result_payload = {
        "job_id": "job-777",
        "dataset_id": dataset_id,
        "version_id": version_id,
        "status": "COMPLETED",
        "extracted_metadata": {"schema_type": "transaction_v1"},
        "completed_at": "2026-09-23T12:00:00Z"
    }
    result_resp = await client.post("/api/v1/catalog/preprocessing-result", json=result_payload)
    assert result_resp.status_code == 200
    result_body = result_resp.json()
    assert result_body["data"]["status"] == "COMPLETED"

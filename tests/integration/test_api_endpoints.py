import pytest
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock

async def test_health_endpoint(test_client: AsyncClient):
    response = await test_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": "2.0.0"}

async def test_register_and_login(test_client: AsyncClient):
    # Register
    reg_resp = await test_client.post("/auth/register", json={
        "email": "newuser@example.com",
        "password": "ValidPassword123!",
        "full_name": "New User"
    })
    assert reg_resp.status_code == 200
    assert "access_token" in reg_resp.json()
    
    # Login
    login_resp = await test_client.post("/auth/login", json={
        "email": "newuser@example.com",
        "password": "ValidPassword123!"
    })
    assert login_resp.status_code == 200
    assert "access_token" in login_resp.json()
    
    # Verify Me
    token = login_resp.json()["access_token"]
    me_resp = await test_client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_resp.status_code == 200
    assert me_resp.json()["email"] == "newuser@example.com"

@patch('server.app.cache_service')
@patch('server.app.process_file_task')
async def test_process_document_endpoint(mock_task, mock_cache, auth_client: AsyncClient):
    # Setup mocks
    mock_cache.compute_hash.return_value = "fake-hash-123"
    mock_cache.get_cached_result = AsyncMock(return_value=None) # No cache hit
    
    # Create dummy file payload
    files = {"file": ("test.txt", b"Dummy document with john@example.com", "text/plain")}
    
    # Upload
    response = await auth_client.post("/process", files=files)
    assert response.status_code == 202
    
    data = response.json()
    assert "job_id" in data
    assert data["status"] == "pending"
    assert data["cached"] is False
    
    # Verify task was dispatched
    mock_task.delay.assert_called_once()
    
    # Check History
    history_resp = await auth_client.get("/history")
    assert history_resp.status_code == 200
    history = history_resp.json()
    assert len(history) > 0
    assert history[0]["job_id"] == data["job_id"]
    assert history[0]["status"] == "pending"

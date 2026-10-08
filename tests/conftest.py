import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


# Use a separate database for automated tests.
os.environ["DATABASE_URL"] = "sqlite:///./test_railway.db"

# Start each pytest run with a clean test database.
test_db = Path("test_railway.db")

if test_db.exists():
    test_db.unlink()


@pytest.fixture
def client():
    from app.main import app

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def user_token(client):
    response = client.post(
        "/auth/login",
        data={
            "username": "testuser_auto@example.com",
            "password": "Test@123",
        },
    )

    assert response.status_code == 200

    return response.json()["access_token"]


@pytest.fixture
def user_headers(user_token):
    return {
        "Authorization": f"Bearer {user_token}"
    }


@pytest.fixture
def admin_token(client):
    response = client.post(
        "/auth/login",
        data={
            "username": "admin@railway.local",
            "password": "Admin@123",
        },
    )

    assert response.status_code == 200

    return response.json()["access_token"]


@pytest.fixture
def admin_headers(admin_token):
    return {
        "Authorization": f"Bearer {admin_token}"
    }
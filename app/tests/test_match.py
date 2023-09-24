from fastapi import status
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app=app)


def test_create_invalid_match_0():
    response = client.post(
        "/matchs",
        json={"match_id": 0, "match_name": "string", "owner_id": 0, "result": "string"},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

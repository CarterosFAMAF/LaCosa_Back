from fastapi import status
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app=app)


def test_create_invalid_match_all_0():
    response = client.post(
        "/matchs",
        json={
            "player_name": "string",
            "match_name": "string",
            "max_players": 0,
            "min_players": 0,
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_create_invalid_match_not_fields():
    response = client.post(
        "/matchs",
        json={},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_create_invalid_match_min_players():
    response = client.post(
        "/matchs",
        json={
            "player_name": "string",
            "match_name": "string",
            "max_players": 4,
            "min_players": 2,
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_create_invalid_match_max_players():
    response = client.post(
        "/matchs",
        json={
            "player_name": "string",
            "match_name": "string",
            "max_players": 13,
            "min_players": 4,
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_create_invalid_match_max_min_players():
    response = client.post(
        "/matchs",
        json={
            "player_name": "string",
            "match_name": "string",
            "max_players": 4,
            "min_players": 5,
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_create_valid_match():
    response = client.post(
        "/matchs",
        json={
            "player_name": "string",
            "match_name": "string",
            "max_players": 12,
            "min_players": 4,
        },
    )
    assert response.status_code == status.HTTP_201_CREATED
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from main import app
from database import get_db

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.json() == {"status": "ok"}


def test_submit():
    mock_conn = MagicMock()
    mock_conn.cursor().fetchone.side_effect = [
        (1,),
        (1, 1, None, ["a", "b", "c", "d", "e", "f", "g", "h"]),
    ]

    def mock_get_db():
        yield mock_conn

    app.dependency_overrides[get_db] = mock_get_db

    response = client.post(
        "/submit",
        json={
            "challenge": "treadmill",
            "answers": ["a", "b", "c", "d", "e", "f", "g", "h"],
        },
    )

    data = response.json()

    assert data["id"] == 1
    assert data["challenge"] == "treadmill"
    assert data["answers"] == ["a", "b", "c", "d", "e", "f", "g", "h"]

    app.dependency_overrides.clear()


def test_get_submissions():
    mock_conn = MagicMock()
    mock_conn.cursor().fetchall.return_value = []

    def mock_get_db():
        yield mock_conn

    app.dependency_overrides[get_db] = mock_get_db

    response = client.get("/submissions")

    data = response.json()

    assert isinstance(data, list)
    assert response.status_code == 200

    app.dependency_overrides.clear()


def test_nominate():
    mock_conn = MagicMock()

    mock_conn.cursor().fetchone.return_value = (1,)

    def mock_get_db():
        yield mock_conn

    app.dependency_overrides[get_db] = mock_get_db

    response = client.post(
        "/nominate",
        json={"name": "john", "email": "john@gmail.com", "submission_id": 12},
    )

    data = response.json()

    assert data["id"] == 1
    assert data["submission_id"] == 12
    assert data["name"] == "john"
    assert data["email"] == "john@gmail.com"

    app.dependency_overrides.clear()


def test_get_nominations():

    mock_conn = MagicMock()
    mock_conn.cursor().fetchall.return_value = []

    def mock_get_db():
        yield mock_conn

    app.dependency_overrides[get_db] = mock_get_db

    response = client.get("/nominations")

    data = response.json()

    assert isinstance(data, list)
    assert response.status_code == 200

    app.dependency_overrides.clear()


def test_stats():
    mock_conn = MagicMock()
    mock_conn.cursor().fetchall.return_value = [
        ("ice bath", 0),
        ("treadmill", 0),
        ("hot wings", 0),
    ]

    def mock_get_db():
        yield mock_conn

    app.dependency_overrides[get_db] = mock_get_db

    response = client.get("/stats")
    data = response.json()
    assert "ice bath" in data
    assert "treadmill" in data
    assert "hot wings" in data

    app.dependency_overrides.clear()

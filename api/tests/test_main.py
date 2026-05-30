from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.json() == {"status": "ok"}


def test_submit():
    response = client.post(
        "/submit",
        json={
            "challenge": "treadmill",
            "answer": ["a", "b", "c", "d", "e", "f", "g", "h"],
        },
    )
    data = response.json()

    assert data["challenge"] == "treadmill"
    assert data["id"] == 1
    assert data["answer"] == ["a", "b", "c", "d", "e", "f", "g", "h"]


def test_get_submissions():
    response = client.get("/submissions")
    assert isinstance(response.json(), list)
    assert response.status_code == 200


def test_nominate():
    response = client.post(
        "/nominate",
        json={
            "nominee_name": "john",
            "nominee_email": "john@gmail.com",
            "submission_id": 12,
        },
    )
    assert response.json() == {
        "nominee_name": "john",
        "nominee_email": "john@gmail.com",
        "submission_id": 12,
    }


def test_get_nominations():
    response = client.get("/nominations")
    assert isinstance(response.json(), list)
    assert response.status_code == 200


def test_stats():
    response = client.get("/stats")
    data = response.json()
    assert "ice bucket" in data
    assert "treadmill" in data
    assert "hot wings" in data

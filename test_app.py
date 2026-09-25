from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health():
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"


def test_homepage():
    response = client.get("/")

    assert response.status_code == 200

    assert "ComicCraft" in response.text


def test_json_validation():
    response = client.post(
        "/generate-comic/json",
        json={
            "story_prompt": "",
            "character_name": "",
            "setting": "",
            "tone": "",
            "art_style": "",
            "panel_count": 5,
        },
    )

    assert response.status_code == 422
    
from time import perf_counter

from fastapi.testclient import TestClient

from app.main import app


def _project_payload() -> dict[str, object]:
    return {
        "project_name": "Sunrise Riverside",
        "property_segment": "apartments",
        "location": "Thu Duc, Ho Chi Minh City",
        "price_range": "3-5B VND",
        "key_selling_points": ["near metro", "river view", "ready handover"],
        "campaign_objective": "lead_generation",
        "buyer_profile": "young families and first-time buyers",
        "tone": "professional_trustworthy",
        "promotion_details": "limited booking incentive",
    }


def test_create_and_retrieve_project_round_trips_through_sqlite(
    tmp_path, monkeypatch
) -> None:
    monkeypatch.setenv(
        "SQLITE_DATABASE_PATH", str(tmp_path / "content_creator.sqlite3")
    )
    client = TestClient(app)

    start = perf_counter()
    create_response = client.post("/projects", json=_project_payload())
    create_duration = perf_counter() - start

    assert create_response.status_code == 201
    create_body = create_response.json()
    assert set(create_body) == {"data", "meta"}
    assert create_body["meta"]["correlation_id"]
    assert create_body["data"]["project_id"]
    assert create_body["data"]["project_name"] == "Sunrise Riverside"
    assert create_body["data"]["brief"]["property_segment"] == "apartments"
    assert create_body["data"]["brief"]["key_selling_points"] == [
        "near metro",
        "river view",
        "ready handover",
    ]
    assert create_body["data"]["created_at"].endswith("Z")
    assert create_body["data"]["updated_at"].endswith("Z")

    project_id = create_body["data"]["project_id"]

    start = perf_counter()
    retrieve_response = client.get(f"/projects/{project_id}")
    retrieve_duration = perf_counter() - start

    assert retrieve_response.status_code == 200
    retrieve_body = retrieve_response.json()
    assert retrieve_body["meta"]["correlation_id"]
    assert retrieve_body["data"] == create_body["data"]
    assert create_duration < 2
    assert retrieve_duration < 2


def test_get_missing_project_returns_standard_not_found_error(
    tmp_path, monkeypatch
) -> None:
    monkeypatch.setenv(
        "SQLITE_DATABASE_PATH", str(tmp_path / "content_creator.sqlite3")
    )
    client = TestClient(app)

    response = client.get("/projects/missing-project")

    assert response.status_code == 404
    body = response.json()
    assert set(body) == {"error", "meta"}
    assert body["error"]["code"] == "not_found"
    assert body["error"]["recoverable"] is True
    assert body["meta"]["correlation_id"]


def test_update_project_replaces_saved_brief(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv(
        "SQLITE_DATABASE_PATH", str(tmp_path / "content_creator.sqlite3")
    )
    client = TestClient(app)
    created = client.post("/projects", json=_project_payload()).json()["data"]

    updated_payload = {
        **_project_payload(),
        "price_range": "4-6B VND",
        "buyer_profile": "investors and young families",
        "key_selling_points": ["near metro", "river view", "new school nearby"],
    }
    response = client.put(f"/projects/{created['project_id']}", json=updated_payload)

    assert response.status_code == 200
    body = response.json()["data"]
    assert body["project_id"] == created["project_id"]
    assert body["brief"]["price_range"] == "4-6B VND"
    assert body["brief"]["buyer_profile"] == "investors and young families"
    assert body["brief"]["key_selling_points"][-1] == "new school nearby"
    assert body["created_at"] == created["created_at"]

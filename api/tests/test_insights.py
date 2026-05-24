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


def _create_project(client: TestClient) -> str:
    response = client.post("/projects", json=_project_payload())
    assert response.status_code == 201
    return response.json()["data"]["project_id"]


def test_collect_and_retrieve_market_insight_snapshot(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv(
        "SQLITE_DATABASE_PATH", str(tmp_path / "content_creator.sqlite3")
    )
    client = TestClient(app)
    project_id = _create_project(client)

    collect_response = client.post(
        f"/projects/{project_id}/insights",
        json={
            "user_context": "Promotion applies to the first booking phase.",
            "approved_source_ids": [],
        },
    )

    assert collect_response.status_code == 201
    body = collect_response.json()
    assert set(body) == {"data", "meta"}
    snapshot = body["data"]
    assert snapshot["project_id"] == project_id
    assert snapshot["status"] == "ready"
    assert snapshot["summary"]
    assert snapshot["confirmed"] is False
    assert "user_provided" in {signal["label"] for signal in snapshot["signals"]}
    assert "project_fact" in {signal["signal_type"] for signal in snapshot["signals"]}

    retrieve_response = client.get(f"/projects/{project_id}/insights")

    assert retrieve_response.status_code == 200
    snapshots = retrieve_response.json()["data"]
    assert len(snapshots) == 1
    assert snapshots[0] == snapshot


def test_update_and_confirm_market_assumptions(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv(
        "SQLITE_DATABASE_PATH", str(tmp_path / "content_creator.sqlite3")
    )
    client = TestClient(app)
    project_id = _create_project(client)
    snapshot = client.post(f"/projects/{project_id}/insights", json={}).json()["data"]

    response = client.patch(
        f"/projects/{project_id}/insights/{snapshot['snapshot_id']}/assumptions",
        json={
            "assumptions": [
                {
                    "question": "Buyer demand",
                    "answer": "Young families prefer projects near metro links.",
                }
            ],
            "confirmed": True,
        },
    )

    assert response.status_code == 200
    updated = response.json()["data"]
    assert updated["confirmed"] is True
    assert {
        "question": "Buyer demand",
        "answer": "Young families prefer projects near metro links.",
    } in updated["assumptions"]
    assert "user_provided" in {signal["label"] for signal in updated["signals"]}


def test_collect_insight_for_missing_project_returns_not_found(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv(
        "SQLITE_DATABASE_PATH", str(tmp_path / "content_creator.sqlite3")
    )
    client = TestClient(app)

    response = client.post("/projects/missing/insights", json={})

    assert response.status_code == 404
    body = response.json()
    assert body["error"]["code"] == "not_found"
    assert body["error"]["recoverable"] is True


def test_internal_project_fact_tool_returns_wrapped_data(
    tmp_path, monkeypatch
) -> None:
    monkeypatch.setenv(
        "SQLITE_DATABASE_PATH", str(tmp_path / "content_creator.sqlite3")
    )
    client = TestClient(app)

    project_facts = client.post(
        "/internal/tools/collect-project-facts",
        json={
            "project_id": "project-1",
            "brief": _project_payload(),
            "user_material_refs": ["sales-kit.pdf"],
            "official_project_url": "https://example.com/project",
        },
    )
    assert project_facts.status_code == 200
    body = project_facts.json()
    assert set(body) == {"data", "meta"}
    assert body["meta"]["correlation_id"]
    assert body["data"]["signals"]


def test_internal_project_tools_return_wrapped_data(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv(
        "SQLITE_DATABASE_PATH", str(tmp_path / "content_creator.sqlite3")
    )
    client = TestClient(app)

    created = client.post(
        "/internal/tools/create-project",
        json=_project_payload(),
    )
    assert created.status_code == 200
    created_body = created.json()
    assert set(created_body) == {"data", "meta"}
    project_id = created_body["data"]["project_id"]

    loaded = client.get(f"/internal/tools/get-project/{project_id}")
    assert loaded.status_code == 200
    loaded_body = loaded.json()
    assert set(loaded_body) == {"data", "meta"}
    assert loaded_body["data"]["project_id"] == project_id

    updated_payload = {
        **_project_payload(),
        "project_id": project_id,
        "buyer_profile": "investors and young families",
    }
    updated = client.post("/internal/tools/update-project", json=updated_payload)
    assert updated.status_code == 200
    updated_body = updated.json()
    assert updated_body["data"]["project_id"] == project_id
    assert updated_body["data"]["brief"]["buyer_profile"] == "investors and young families"


def test_internal_workflow_tools_return_wrapped_epic2_and_epic3_bundles(
    tmp_path, monkeypatch
) -> None:
    monkeypatch.setenv(
        "SQLITE_DATABASE_PATH", str(tmp_path / "content_creator.sqlite3")
    )
    client = TestClient(app)
    project_id = _create_project(client)

    insight_workflow = client.post(
        "/internal/tools/collect-insight-workflow",
        json={
            "project_id": project_id,
            "user_context": "Metro demand remains strong for young families.",
            "official_project_url": "https://example.com/project",
        },
    )
    assert insight_workflow.status_code == 200
    insight_body = insight_workflow.json()
    assert set(insight_body) == {"data", "meta"}
    assert insight_body["data"]["project_id"] == project_id
    assert len(insight_body["data"]["questions"]) == 5
    assert insight_body["data"]["project_facts"]["signals"]
    assert insight_body["data"]["market_signals"]["signals"]

    confirmed = client.post(
        "/internal/tools/confirm-market-assumptions",
        json={
            "project_id": project_id,
            "insight_snapshot_id": insight_body["data"]["insight_snapshot_id"],
            "assumptions": [
                {
                    "question": "Buyer demand",
                    "answer": "Use user-confirmed second-home demand as an assumption.",
                }
            ],
            "confirmed": True,
        },
    )
    assert confirmed.status_code == 200
    confirmed_body = confirmed.json()["data"]
    assert confirmed_body["insight_snapshot_id"] == insight_body["data"]["insight_snapshot_id"]
    assert confirmed_body["confirmed"] is True

    campaign_context = client.post(
        "/internal/tools/prepare-campaign-context",
        json={
            "project_id": project_id,
            "insight_summary": insight_body["data"]["insight_summary"],
            "planning_constraints": {
                "total_budget_vnd": 120000000,
                "target_leads": 240,
                "campaign_days": 30,
            },
            "unavailable_signals": insight_body["data"]["unavailable_signals"],
        },
    )
    assert campaign_context.status_code == 200
    context_body = campaign_context.json()
    assert set(context_body) == {"data", "meta"}
    assert context_body["data"]["project_id"] == project_id
    assert context_body["data"]["strategy"]["rule_version"] == "campaign-strategy-v1"
    assert context_body["data"]["campaign_plan"]["rule_version"] == "campaign-planning-v1"


def test_internal_workflow_tools_return_not_found_for_missing_project(
    tmp_path, monkeypatch
) -> None:
    monkeypatch.setenv(
        "SQLITE_DATABASE_PATH", str(tmp_path / "content_creator.sqlite3")
    )
    client = TestClient(app)

    insight_workflow = client.post(
        "/internal/tools/collect-insight-workflow",
        json={"project_id": "missing-project"},
    )
    assert insight_workflow.status_code == 404
    assert insight_workflow.json()["error"]["code"] == "not_found"

    campaign_context = client.post(
        "/internal/tools/prepare-campaign-context",
        json={
            "project_id": "missing-project",
            "insight_summary": "summary",
        },
    )
    assert campaign_context.status_code == 404
    assert campaign_context.json()["error"]["code"] == "not_found"

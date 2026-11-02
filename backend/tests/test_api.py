from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_network_endpoint():
    response = client.get("/api/network")
    assert response.status_code == 200
    assert len(response.json()["nodes"]) >= 8


def test_route_endpoint():
    result = client.post("/api/route", json={"start":"west", "destination":"science"})
    assert result.status_code == 200
    assert result.json()["node_ids"][0] == "west"
    assert result.json()["node_ids"][-1] == "science"


def test_invalid_node():
    result = client.post("/api/route", json={"start":"unknown", "destination":"west"})
    assert result.status_code == 422


def test_obstruction_report_stays_pending():
    result = client.post("/api/reports", json={"edge_id":"west-library","description":"Temporary construction at this segment"})
    assert result.status_code == 201
    assert result.json()["status"] == "pending_review"
    reported = client.get("/api/reports").json()
    assert any(row["id"] == result.json()["id"] for row in reported)

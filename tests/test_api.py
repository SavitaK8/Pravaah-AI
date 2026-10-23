from fastapi.testclient import TestClient

from pravaah.main import app


def test_api_flow():
    with TestClient(app) as c:
        assert set(c.get("/api/venue").json()) == {"zones", "edges"}
        s = c.get("/api/state").json()
        assert s["zones"]["Gate A"]["forecast"] and s["predictor"] == "linear-trend"
        r = c.get("/api/route", params={"src": "Parking 1", "dst": "Zone 1"}).json()
        assert r["path"][0] == "Parking 1" and r["path"][-1] == "Zone 1"
        assert c.get("/api/route", params={"src": "x", "dst": "Zone 1"}).status_code == 404
        assert c.post("/api/alerts/gate-a-high/approve").json() == {"ok": True}
        assert "Pravaah AI" in c.get("/").text


def test_websocket_pushes_state():
    with TestClient(app) as c, c.websocket_connect("/ws") as ws:
        assert "zones" in ws.receive_json()
        assert ws.receive_json()["t"] >= 1

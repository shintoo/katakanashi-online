import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from app.main import app

ICON = {"shape": 1, "color": "#3ec5ff"}
client: TestClient


# One shared client keeps every socket on the same event loop.
@pytest.fixture(scope="module", autouse=True)
def shared_client():
    global client
    with TestClient(app) as client:
        yield


def latest_state(ws, until=lambda s: True):
    while True:
        msg = ws.receive_json()
        if msg["type"] == "state" and until(msg["state"]):
            return msg["state"]


def test_health():
    assert client.get("/api/health").json() == {"ok": True}


def test_join_errors():
    assert client.get("/api/rooms/ZZZZ").status_code == 404
    assert client.post("/api/rooms", json={"name": "", "icon": ICON}).status_code == 400


def test_bad_token_is_rejected():
    room = client.post("/api/rooms", json={"name": "Host", "icon": ICON}).json()
    with pytest.raises(WebSocketDisconnect) as e:
        with client.websocket_connect(f"/ws/{room['code']}?token=nope") as ws:
            ws.receive_json()
    assert e.value.code == 4401


def test_full_turn_over_sockets():
    host = client.post("/api/rooms", json={"name": "Host", "icon": ICON}).json()
    code = host["code"]
    assert client.get(f"/api/rooms/{code.lower()}").status_code == 200
    guest = client.post(f"/api/rooms/{code}/players", json={"name": "Guest", "icon": ICON}).json()

    with client.websocket_connect(f"/ws/{code}?token={host['token']}") as hws:
        assert latest_state(hws)["you"] == host["id"]
        with client.websocket_connect(f"/ws/{code}?token={guest['token']}") as gws:
            latest_state(gws)
            latest_state(hws)
            hws.send_json({"type": "start", "settings": {"rounds": 1, "time_limit": 30, "first": "host"}})
            assert latest_state(hws)["phase"] == "playing"
            latest_state(gws)

            gws.send_json({"type": "draw"})
            assert gws.receive_json()["type"] == "error"

            hws.send_json({"type": "draw"})
            mine = latest_state(hws)
            theirs = latest_state(gws)
            assert len(mine["hand"]["words"]) == 6 and mine["hand"]["target"] in range(1, 7)
            assert "words" not in theirs["hand"] and theirs["time_left"] <= 30

            hws.send_json({"type": "give", "to": guest["id"]})
            s = latest_state(gws)
            assert s["players"][1]["score"] == 1 and s["describer"] == guest["id"]

        latest_state(hws, until=lambda s: not s["players"][1]["connected"])

        # Coming back with the same token puts the guest back in their seat.
        with client.websocket_connect(f"/ws/{code}?token={guest['token']}") as gws:
            s = latest_state(gws)
            assert s["you"] == guest["id"] and s["players"][1]["score"] == 1
            assert s["players"][1]["connected"]


def test_removed_player_is_kicked():
    host = client.post("/api/rooms", json={"name": "Host", "icon": ICON}).json()
    code = host["code"]
    guest = client.post(f"/api/rooms/{code}/players", json={"name": "Guest", "icon": ICON}).json()
    with client.websocket_connect(f"/ws/{code}?token={host['token']}") as hws:
        latest_state(hws)
        with client.websocket_connect(f"/ws/{code}?token={guest['token']}") as gws:
            latest_state(gws)
            hws.send_json({"type": "remove", "id": guest["id"]})
            msgs = []
            with pytest.raises(WebSocketDisconnect):
                while True:
                    msgs.append(gws.receive_json())
            assert {"type": "removed"} in msgs
        latest_state(hws, until=lambda s: len(s["players"]) == 1)


def test_close_room():
    host = client.post("/api/rooms", json={"name": "Host", "icon": ICON}).json()
    code = host["code"]
    with client.websocket_connect(f"/ws/{code}?token={host['token']}") as hws:
        latest_state(hws)
        hws.send_json({"type": "close"})
        assert hws.receive_json() == {"type": "closed"}
    assert client.get(f"/api/rooms/{code}").status_code == 404

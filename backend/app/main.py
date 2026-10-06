import time
from pathlib import Path

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.websockets import WebSocketState
from pydantic import BaseModel

from .game import GameError
from .hub import Hub

app = FastAPI(title="Katakanashi Online")
hub = Hub()


class JoinBody(BaseModel):
    name: str = ""
    icon: dict = {}


@app.get("/api/health")
def health():
    return {"ok": True}


@app.post("/api/rooms")
async def create_room(body: JoinBody):
    live = hub.create()
    try:
        p = live.room.add_player(body.name, body.icon, time.monotonic())
    except GameError as e:
        hub.rooms.pop(live.room.code, None)
        raise HTTPException(400, str(e))
    return {"code": live.room.code, "token": p.token, "id": p.id}


@app.get("/api/rooms/{code}")
async def room_info(code: str):
    live = hub.get(code)
    if not live:
        raise HTTPException(404, "There's no room with that code.")
    room = live.room
    return {"code": room.code, "players": len(room.players), "phase": room.phase}


@app.post("/api/rooms/{code}/players")
async def join_room(code: str, body: JoinBody):
    live = hub.get(code)
    if not live:
        raise HTTPException(404, "There's no room with that code.")
    try:
        p = live.room.add_player(body.name, body.icon, time.monotonic())
    except GameError as e:
        raise HTTPException(400, str(e))
    await live.flush()
    return {"code": live.room.code, "token": p.token, "id": p.id}


@app.websocket("/ws/{code}")
async def room_socket(websocket: WebSocket, code: str, token: str = ""):
    await websocket.accept()
    live = hub.get(code)
    if not live:
        await websocket.close(code=4404)
        return
    player = live.room.by_token(token)
    if not player:
        await websocket.close(code=4401)
        return
    live.sockets.setdefault(player.id, set()).add(websocket)
    live.room.connect(player, time.monotonic())
    await live.flush()
    try:
        while websocket.application_state == WebSocketState.CONNECTED:
            msg = await websocket.receive_json()
            if not isinstance(msg, dict):
                continue
            # The player may have been removed while this socket was open.
            if live.room.player(player.id) is None or hub.get(code) is not live:
                break
            try:
                await live.handle(player, msg)
            except GameError as e:
                await websocket.send_json({"type": "error", "message": str(e)})
    except WebSocketDisconnect:
        pass
    finally:
        socks = live.sockets.get(player.id)
        if socks is not None:
            socks.discard(websocket)
        if live.room.player(player.id) is not None:
            live.room.disconnect(player, time.monotonic())
            if hub.get(code) is live:
                await live.flush()


# In production, serve the built frontend from the same server.
DIST = Path(__file__).resolve().parents[2] / "frontend" / "dist"
if DIST.exists():
    app.mount("/assets", StaticFiles(directory=DIST / "assets"), name="assets")

    @app.get("/{path:path}")
    async def spa(path: str):
        file = DIST / path
        if path and file.is_file() and DIST in file.resolve().parents:
            return FileResponse(file)
        return FileResponse(DIST / "index.html")

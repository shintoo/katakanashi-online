from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI(title="Katakanashi Online")


@app.get("/api/health")
def health():
    return {"ok": True}


@app.websocket("/ws")
async def ws(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            msg = await websocket.receive_json()
            if msg.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        pass

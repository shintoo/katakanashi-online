"""Keeps rooms in memory, tracks each player's open sockets, and pushes updates."""

import asyncio
import random
import time

from fastapi import WebSocket

from .game import CODE_DIGITS, CODE_LETTERS, GameError, Room


class LiveRoom:
    def __init__(self, hub, room: Room):
        self.hub = hub
        self.room = room
        self.sockets: dict[str, set[WebSocket]] = {}
        self.timer: asyncio.Task | None = None

    async def flush(self):
        """Send pending events and a fresh view to everyone, then re-arm the timer."""
        room = self.room
        events = room.take_events()
        now = time.monotonic()
        for pid, socks in list(self.sockets.items()):
            msgs = [{"type": "event", **e} for e in events]
            if room.closed:
                msgs.append({"type": "closed"})
            else:
                msgs.append({"type": "state", "state": room.view(pid, now)})
            for ws in list(socks):
                try:
                    for m in msgs:
                        await ws.send_json(m)
                except Exception:
                    pass
        if room.closed:
            await self.shutdown()
        else:
            self.rearm()

    def rearm(self):
        if self.timer:
            self.timer.cancel()
        when = self.room.next_wakeup()
        if when is not None:
            self.timer = asyncio.create_task(self._wake(when))

    async def _wake(self, when):
        await asyncio.sleep(max(0.0, when - time.monotonic()))
        self.timer = None
        if not self.room.tick(time.monotonic()):
            await self.shutdown()
            return
        await self.flush()

    async def shutdown(self):
        self.hub.rooms.pop(self.room.code, None)
        if self.timer and self.timer is not asyncio.current_task():
            self.timer.cancel()
        for socks in self.sockets.values():
            for ws in list(socks):
                try:
                    await ws.close(code=4404)
                except Exception:
                    pass
        self.sockets.clear()

    async def kick(self, pid):
        for ws in list(self.sockets.pop(pid, ())):
            try:
                await ws.send_json({"type": "removed"})
                await ws.close(code=4403)
            except Exception:
                pass

    async def handle(self, player, msg):
        room, now = self.room, time.monotonic()
        kind = msg.get("type")
        if kind == "ping":
            return
        actions = {
            "settings": lambda: room.update_settings(player, msg.get("settings")),
            "color": lambda: room.set_color(player, msg.get("color")),
            "start": lambda: room.start(player, now, msg.get("settings")),
            "spin": lambda: room.spin(player),
            "begin": lambda: room.begin(player),
            "draw": lambda: room.draw(player, now),
            "give": lambda: room.give(player, msg.get("to"), now),
            "next_round": lambda: room.next_round(player),
            "end_game": lambda: room.end_game(player),
            "move_card": lambda: room.move_card(player, msg.get("from"), msg.get("to")),
            "remove": lambda: room.remove_player(player, msg.get("id"), now),
            "close": lambda: room.close(player),
        }
        if kind not in actions:
            raise GameError("Unknown action.")
        result = actions[kind]()
        if kind == "remove":
            await self.kick(result.id)
        await self.flush()


class Hub:
    def __init__(self, rng=None):
        self.rng = rng or random.Random()
        self.rooms: dict[str, LiveRoom] = {}

    def new_code(self):
        while True:
            code = "".join(self.rng.choice(chars) for chars in (CODE_LETTERS, CODE_DIGITS) * 2)
            if code not in self.rooms:
                return code

    def create(self):
        code = self.new_code()
        live = LiveRoom(self, Room(code, time.monotonic()))
        self.rooms[code] = live
        live.rearm()
        return live

    def get(self, code):
        return self.rooms.get((code or "").upper())

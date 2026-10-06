"""Room and game rules. Plain synchronous logic: callers pass in the current time."""

import random
import secrets
from dataclasses import dataclass, field

from .words import CARDS

TABLE_COLORS = [
    "#b49cff", "#3ecfb2", "#ff8a7a", "#6cc4ff", "#8ee3a5",
    "#ffd35c", "#ff9ccf", "#ffad5c", "#8fa5ff", "#c6e86b",
]
PLAYER_COLORS = [
    "#ffd23f", "#ff5fa2", "#3ec5ff", "#5ee07a", "#ff8c42",
    "#7b5cff", "#ff4d6d", "#2ee6d6", "#c08bff", "#a3e635",
]
ICON_SHAPES = 5
TIME_LIMITS = (30, 60, 120, 300, None)
MAX_PLAYERS = 10
MAX_NAME = 14
MAX_ROUNDS = 20

# How long to wait before acting on a dropped connection.
SKIP_GRACE = 10.0
HOST_GRACE = 60.0
EMPTY_ROOM_TTL = 30 * 60.0

CODE_LETTERS = "ABCDEFGHJKLMNPQRSTUVWXYZ"
# Codes go letter-number-letter-number so they can never spell a word.
CODE_DIGITS = "23456789"


class GameError(Exception):
    pass


@dataclass
class Card:
    words: list
    number: int


@dataclass
class Player:
    id: str
    token: str
    name: str
    icon: dict
    won: list = field(default_factory=list)
    sockets: int = 0
    left_at: float | None = None

    @property
    def connected(self):
        return self.sockets > 0


def default_settings():
    return {"rounds": 5, "time_limit": 60, "first": "random"}


def clean_settings(raw):
    s = default_settings()
    if not isinstance(raw, dict):
        raise GameError("Bad settings.")
    rounds = raw.get("rounds", s["rounds"])
    if rounds is not None and (not isinstance(rounds, int) or not 1 <= rounds <= MAX_ROUNDS):
        raise GameError("Rounds must be between 1 and 20, or endless.")
    time_limit = raw.get("time_limit", s["time_limit"])
    if time_limit not in TIME_LIMITS:
        raise GameError("That time limit isn't an option.")
    first = raw.get("first", s["first"])
    if first not in ("random", "host"):
        raise GameError("First player must be random or host.")
    return {"rounds": rounds, "time_limit": time_limit, "first": first}


def clean_name(name):
    if not isinstance(name, str):
        raise GameError("Please enter a name.")
    name = " ".join(name.split())
    if not name:
        raise GameError("Please enter a name.")
    if len(name) > MAX_NAME:
        raise GameError(f"Names can be up to {MAX_NAME} letters.")
    return name


def clean_icon(icon):
    if not isinstance(icon, dict):
        raise GameError("Please pick an icon.")
    shape, color = icon.get("shape"), icon.get("color")
    if not isinstance(shape, int) or not 0 <= shape < ICON_SHAPES or color not in PLAYER_COLORS:
        raise GameError("Please pick an icon.")
    return {"shape": shape, "color": color}


def new_deck(rng):
    cards = [Card(words=[list(w) for w in words], number=rng.randint(1, 6)) for _, words in CARDS]
    rng.shuffle(cards)
    return cards


class Room:
    def __init__(self, code, now, rng=None):
        self.code = code
        self.rng = rng or random.Random()
        self.players: list[Player] = []
        self.host_id = None
        self.settings = default_settings()
        self.table_color = self.rng.choice(TABLE_COLORS)
        self.phase = "lobby"  # lobby, picking, playing, round_end, ended
        self.round = 0
        self.deck: list[Card] = []
        self.discard: list[Card] = []
        self.describer_id = None
        self.round_start_id = None
        self.turns_this_round = 0
        self.hand: Card | None = None
        self.target = None
        self.deadline = None
        self.wheel = None
        self.events = []
        self.empty_since = now
        self.closed = False

    # ---------- players ----------

    def player(self, pid):
        for p in self.players:
            if p.id == pid:
                return p
        return None

    def by_token(self, token):
        for p in self.players:
            if p.token == token:
                return p
        return None

    def index(self, pid):
        return next(i for i, p in enumerate(self.players) if p.id == pid)

    def add_player(self, name, icon, now):
        name, icon = clean_name(name), clean_icon(icon)
        if len(self.players) >= MAX_PLAYERS:
            raise GameError("This room is full.")
        if any(p.name.lower() == name.lower() for p in self.players):
            raise GameError("Someone in this room already has that name.")
        p = Player(id=secrets.token_hex(4), token=secrets.token_urlsafe(18), name=name, icon=icon, left_at=now)
        self.players.append(p)
        if self.host_id is None:
            self.host_id = p.id
        else:
            self.emit("joined", name=name)
        return p

    def connect(self, p, now):
        p.sockets += 1
        p.left_at = None
        self.empty_since = None

    def disconnect(self, p, now):
        p.sockets = max(0, p.sockets - 1)
        if not p.connected:
            p.left_at = now
            if not any(q.connected for q in self.players):
                self.empty_since = now

    def remove_player(self, by, pid, now):
        self.require_host(by)
        p = self.player(pid)
        if p is None:
            raise GameError("That player isn't here.")
        if p.id == self.host_id:
            raise GameError("The host can't remove themselves.")
        was_describer = p.id == self.describer_id
        if was_describer and self.hand:
            self.discard.append(self.hand)
            self.hand = None
        self.discard.extend(p.won)
        was_start = p.id == self.round_start_id
        if was_start:
            self.round_start_id = self.players[(self.index(p.id) + 1) % len(self.players)].id
        if was_describer and self.phase == "playing":
            # If they were starting the round, the round hasn't really begun, so don't end it.
            self.advance(now, skip_from=p.id, can_wrap=not was_start)
        elif was_describer:
            self.describer_id = self.players[(self.index(p.id) + 1) % len(self.players)].id
        self.players.remove(p)
        if self.wheel and self.wheel.get("winner") == p.id:
            self.wheel = None
        self.emit("removed", name=p.name)
        if self.phase in ("picking", "playing", "round_end") and len(self.players) < 2:
            self.finish()
        return p

    # ---------- host actions ----------

    def require_host(self, by):
        if by.id != self.host_id:
            raise GameError("Only the host can do that.")

    def update_settings(self, by, raw):
        self.require_host(by)
        if self.phase not in ("lobby", "ended"):
            raise GameError("Settings can only change before a game.")
        self.settings = clean_settings(raw)

    def set_color(self, by, color):
        self.require_host(by)
        if color not in TABLE_COLORS:
            raise GameError("That color isn't an option.")
        self.table_color = color

    def start(self, by, now, raw_settings=None):
        self.require_host(by)
        if self.phase not in ("lobby", "ended"):
            raise GameError("A game is already going.")
        if raw_settings is not None:
            self.settings = clean_settings(raw_settings)
        if len(self.players) < 2:
            raise GameError("You need at least 2 players.")
        for p in self.players:
            p.won = []
        self.deck = new_deck(self.rng)
        self.discard = []
        self.hand = None
        self.target = None
        self.deadline = None
        self.round = 1
        self.turns_this_round = 0
        if self.settings["first"] == "host":
            self.begin_with(self.host_id)
        else:
            self.phase = "picking"
            self.wheel = {"winner": None, "spin": 0}
            self.describer_id = None

    def spin(self, by):
        self.require_host(by)
        if self.phase != "picking" or self.wheel["winner"]:
            raise GameError("The wheel can't spin right now.")
        choices = [p for p in self.players if p.connected] or self.players
        winner = self.rng.choice(choices)
        self.wheel = {"winner": winner.id, "spin": self.rng.random()}

    def begin(self, by):
        self.require_host(by)
        if self.phase != "picking" or not self.wheel["winner"]:
            raise GameError("Spin the wheel first.")
        self.begin_with(self.wheel["winner"])

    def begin_with(self, pid):
        self.phase = "playing"
        self.wheel = None
        self.describer_id = pid
        self.round_start_id = pid
        self.emit("first", id=pid)

    def next_round(self, by):
        self.require_host(by)
        if self.phase != "round_end":
            raise GameError("The round isn't over yet.")
        self.round += 1
        self.turns_this_round = 0
        self.phase = "playing"
        self.emit("round", n=self.round)

    def can_end(self):
        return self.phase == "round_end" or (
            self.phase == "playing" and self.hand is None and self.turns_this_round == 0
        )

    def end_game(self, by):
        self.require_host(by)
        if not self.can_end():
            raise GameError("You can end the game between rounds.")
        self.finish()

    def move_card(self, by, from_id, to_id):
        self.require_host(by)
        a, b = self.player(from_id), self.player(to_id)
        if a is None or b is None or a is b:
            raise GameError("Pick two different players.")
        if not a.won:
            raise GameError(f"{a.name} has no cards to move.")
        b.won.append(a.won.pop())
        self.emit("moved", **{"from": a.id, "to": b.id})

    def close(self, by):
        self.require_host(by)
        self.closed = True

    # ---------- turns ----------

    def require_describer(self, by):
        if self.phase != "playing" or by.id != self.describer_id:
            raise GameError("It's not your turn.")

    def draw(self, by, now):
        self.require_describer(by)
        if self.hand:
            raise GameError("You already have a card.")
        if len(self.deck) < 2 and self.discard:
            self.reshuffle()
        if len(self.deck) < 2:
            self.finish()
            return
        self.hand = self.deck.pop(0)
        self.target = self.deck[0].number
        limit = self.settings["time_limit"]
        self.deadline = now + limit if limit else None
        self.emit("drew", by=by.id)

    def reshuffle(self):
        for c in self.discard:
            c.number = self.rng.randint(1, 6)
        self.rng.shuffle(self.discard)
        self.deck.extend(self.discard)
        self.discard = []
        self.emit("shuffled")

    def give(self, by, to_id, now):
        self.require_describer(by)
        if not self.hand:
            raise GameError("Draw a card first.")
        if to_id is None:
            self.discard.append(self.hand)
            self.emit("discarded", by=by.id)
        else:
            to = self.player(to_id)
            if to is None or to is by:
                raise GameError("Pick another player.")
            to.won.append(self.hand)
            self.emit("gave", **{"from": by.id, "to": to.id})
        self.hand = None
        self.turns_this_round += 1
        self.advance(now)

    def advance(self, now, skip_from=None, can_wrap=True):
        """Move to the next connected player, handling the end of a round."""
        self.hand = None
        self.target = None
        self.deadline = None
        n = len(self.players)
        i = self.index(skip_from or self.describer_id)
        start = self.index(self.round_start_id)
        wrapped = False
        nxt = None
        for step in range(1, n + 1):
            j = (i + step) % n
            if j == start:
                wrapped = True
            if self.players[j].connected and self.players[j].id != skip_from:
                nxt = self.players[j]
                break
        if nxt is None:
            nxt = self.players[(i + 1) % n]
            wrapped = wrapped or (i + 1) % n == start
        self.describer_id = nxt.id
        if not wrapped or not can_wrap:
            return
        if self.settings["rounds"] and self.round >= self.settings["rounds"]:
            self.finish()
        elif self.settings["rounds"] is None:
            self.phase = "round_end"
        else:
            self.round += 1
            self.turns_this_round = 0
            self.emit("round", n=self.round)

    def finish(self):
        if self.hand:
            self.discard.append(self.hand)
        self.hand = None
        self.target = None
        self.deadline = None
        self.wheel = None
        self.phase = "ended"
        self.emit("ended")

    # ---------- time ----------

    def next_wakeup(self):
        times = []
        if self.empty_since is not None:
            times.append(self.empty_since + EMPTY_ROOM_TTL)
        host = self.player(self.host_id)
        if host and host.left_at is not None and any(p.connected for p in self.players):
            times.append(host.left_at + HOST_GRACE)
        d = self.player(self.describer_id)
        if self.phase == "playing" and not self.hand and d and d.left_at is not None:
            if any(p.connected for p in self.players):
                times.append(d.left_at + SKIP_GRACE)
        return min(times) if times else None

    def tick(self, now):
        """Handle anything that was waiting on a timer. Returns False if the room should be deleted."""
        if self.empty_since is not None and now >= self.empty_since + EMPTY_ROOM_TTL:
            return False
        host = self.player(self.host_id)
        if host and host.left_at is not None and now >= host.left_at + HOST_GRACE:
            heir = next((p for p in self.players if p.connected), None)
            if heir:
                self.host_id = heir.id
                self.emit("host", id=heir.id)
        d = self.player(self.describer_id)
        if self.phase == "playing" and not self.hand and d and d.left_at is not None:
            if now >= d.left_at + SKIP_GRACE and any(p.connected for p in self.players):
                self.emit("skipped", name=d.name)
                self.advance(now)
        return True

    # ---------- output ----------

    def emit(self, kind, **data):
        self.events.append({"kind": kind, **data})

    def take_events(self):
        events, self.events = self.events, []
        return events

    def view(self, pid, now):
        """What one player is allowed to see."""
        me = self.player(pid)
        describing = me is not None and me.id == self.describer_id
        hand = None
        if self.hand:
            hand = {"number": self.hand.number}
            if describing:
                hand["words"] = self.hand.words
                hand["target"] = self.target
        return {
            "code": self.code,
            "you": pid,
            "host": self.host_id,
            "phase": self.phase,
            "settings": self.settings,
            "table_color": self.table_color,
            "round": self.round,
            "players": [
                {
                    "id": p.id,
                    "name": p.name,
                    "icon": p.icon,
                    "score": len(p.won),
                    "connected": p.connected,
                }
                for p in self.players
            ],
            "describer": self.describer_id,
            "round_start": self.round_start_id,
            "deck_count": len(self.deck),
            "top_number": self.deck[0].number if self.deck else None,
            "discard_count": len(self.discard),
            "discard_number": self.discard[-1].number if self.discard else None,
            "hand": hand,
            "time_left": max(0.0, self.deadline - now) if self.deadline else None,
            "wheel": self.wheel,
            "can_end": self.can_end(),
        }

import random

import pytest

from app.words import CARDS
from app.game import EMPTY_ROOM_TTL, HOST_GRACE, SKIP_GRACE, GameError, Room

ICON = {"shape": 0, "color": "#ffd23f"}


def make_room(n=3, settings=None, connect=True):
    room = Room("TEST", now=0, rng=random.Random(1))
    players = [room.add_player(f"P{i}", ICON, 0) for i in range(n)]
    if connect:
        for p in players:
            room.connect(p, 0)
    room.settings.update(settings or {"first": "host"})
    room.take_events()
    return room, players


def play_turn(room, to=None, now=0):
    d = room.player(room.describer_id)
    room.draw(d, now)
    if to is None:
        to = next(p for p in room.players if p is not d)
    room.give(d, to.id if to else None, now)


def test_first_player_is_host():
    room, (a, b, c) = make_room()
    assert a.id == room.host_id
    room.start(a, 0)
    assert room.phase == "playing" and room.describer_id == a.id


def test_only_host_starts_and_needs_two_players():
    room, (a, b, c) = make_room()
    with pytest.raises(GameError):
        room.start(b, 0)
    solo, (x,) = make_room(1)
    with pytest.raises(GameError):
        solo.start(x, 0)


def test_wheel_picks_a_player():
    room, (a, b, c) = make_room(settings={"first": "random"})
    room.start(a, 0)
    assert room.phase == "picking"
    with pytest.raises(GameError):
        room.begin(a)
    room.spin(a)
    winner = room.wheel["winner"]
    room.begin(a)
    assert room.phase == "playing" and room.describer_id == winner == room.round_start_id


def test_draw_picks_word_from_next_card():
    room, (a, b, c) = make_room()
    room.start(a, 0)
    next_number = room.deck[1].number
    room.draw(a, 0)
    assert room.target == next_number
    assert room.deadline == 60


def test_only_describer_sees_words():
    room, (a, b, c) = make_room()
    room.start(a, 0)
    room.draw(a, 0)
    assert "words" in room.view(a.id, 0)["hand"]
    other = room.view(b.id, 0)["hand"]
    assert "words" not in other and "target" not in other
    assert "words" not in str(room.view(b.id, 0))


def test_category_never_sent():
    room, (a, b, c) = make_room()
    room.start(a, 0)
    room.draw(a, 0)
    categories = {cat for cat, _ in CARDS}

    def strings(x):
        if isinstance(x, str):
            yield x
        elif isinstance(x, dict):
            for v in x.values():
                yield from strings(v)
        elif isinstance(x, list):
            for v in x:
                yield from strings(v)

    assert not categories & set(strings(room.view(a.id, 0)))


def test_give_scores_and_moves_turn():
    room, (a, b, c) = make_room()
    room.start(a, 0)
    play_turn(room, to=c)
    assert len(c.won) == 1 and room.describer_id == b.id
    with pytest.raises(GameError):
        room.draw(a, 0)


def test_cannot_give_to_self():
    room, (a, b, c) = make_room()
    room.start(a, 0)
    room.draw(a, 0)
    with pytest.raises(GameError):
        room.give(a, a.id, 0)


def test_nobody_got_it_goes_to_discard():
    room, (a, b, c) = make_room()
    room.start(a, 0)
    room.draw(a, 0)
    room.give(a, None, 0)
    assert len(room.discard) == 1


def test_rounds_advance_and_game_ends():
    room, (a, b, c) = make_room(settings={"first": "host", "rounds": 2})
    room.start(a, 0)
    for _ in range(3):
        play_turn(room)
    assert room.round == 2 and room.phase == "playing" and room.describer_id == a.id
    for _ in range(3):
        play_turn(room)
    assert room.phase == "ended"


def test_endless_asks_host_each_round():
    room, (a, b, c) = make_room(settings={"first": "host", "rounds": None})
    room.start(a, 0)
    for _ in range(3):
        play_turn(room)
    assert room.phase == "round_end" and room.can_end()
    room.next_round(a)
    assert room.round == 2 and room.phase == "playing"
    play_turn(room)
    with pytest.raises(GameError):
        room.end_game(a)


def test_end_game_between_rounds():
    room, (a, b, c) = make_room(settings={"first": "host", "rounds": None})
    room.start(a, 0)
    for _ in range(3):
        play_turn(room)
    room.end_game(a)
    assert room.phase == "ended"


def test_discard_reshuffles_when_deck_runs_low():
    room, (a, b, c) = make_room(settings={"first": "host", "rounds": None})
    room.start(a, 0)
    room.discard, room.deck = room.deck[1:], room.deck[:1]
    play_turn(room)
    assert room.phase != "ended"
    assert any(e["kind"] == "shuffled" for e in room.take_events())


def test_game_ends_when_cards_run_out():
    room, (a, b, c) = make_room(settings={"first": "host", "rounds": None})
    room.start(a, 0)
    room.deck, room.discard = room.deck[:1], []
    room.draw(a, 0)
    assert room.phase == "ended"


def test_disconnected_player_is_skipped():
    room, (a, b, c) = make_room()
    room.start(a, 0)
    room.disconnect(b, 0)
    play_turn(room, to=c)
    assert room.describer_id == c.id


def test_describer_who_drops_is_skipped_after_grace():
    room, (a, b, c) = make_room()
    room.start(a, 0)
    room.disconnect(a, 5)
    assert room.next_wakeup() == 5 + SKIP_GRACE
    room.tick(5 + SKIP_GRACE - 1)
    assert room.describer_id == a.id
    room.connect(a, 6)
    room.tick(5 + SKIP_GRACE)
    assert room.describer_id == a.id
    room.disconnect(a, 20)
    room.tick(20 + SKIP_GRACE)
    assert room.describer_id == b.id


def test_reconnect_keeps_seat_and_cards():
    room, (a, b, c) = make_room()
    room.start(a, 0)
    play_turn(room, to=b)
    room.disconnect(b, 1)
    assert room.by_token(b.token) is b
    room.connect(b, 2)
    assert room.view(b.id, 2)["players"][1]["score"] == 1


def test_host_moves_card():
    room, (a, b, c) = make_room()
    room.start(a, 0)
    play_turn(room, to=b)
    with pytest.raises(GameError):
        room.move_card(b, b.id, c.id)
    room.move_card(a, b.id, c.id)
    assert len(b.won) == 0 and len(c.won) == 1


def test_remove_player():
    room, (a, b, c) = make_room()
    room.start(a, 0)
    play_turn(room, to=c)
    room.draw(b, 0)
    room.remove_player(a, b.id, 0)
    assert room.player(b.id) is None and room.describer_id == c.id
    assert room.hand is None and len(room.discard) == 1
    with pytest.raises(GameError):
        room.remove_player(a, a.id, 0)


def test_removing_round_starter_on_their_turn_keeps_round():
    room, (a, b, c) = make_room(settings={"first": "host", "rounds": 3})
    room.start(a, 0)
    for _ in range(3):
        play_turn(room)
    assert room.round == 2 and room.describer_id == a.id
    room.host_id = c.id
    room.remove_player(c, a.id, 0)
    assert room.round == 2 and room.describer_id == b.id and room.round_start_id == b.id


def test_removing_down_to_one_player_ends_game():
    room, (a, b) = make_room(2)
    room.start(a, 0)
    room.remove_player(a, b.id, 0)
    assert room.phase == "ended"


def test_host_passes_on_after_leaving():
    room, (a, b, c) = make_room()
    room.disconnect(a, 0)
    room.tick(HOST_GRACE)
    assert room.host_id == b.id


def test_empty_room_expires():
    room, players = make_room()
    for p in players:
        room.disconnect(p, 0)
    assert room.tick(EMPTY_ROOM_TTL - 1)
    assert not room.tick(EMPTY_ROOM_TTL)


def test_play_again_resets_scores():
    room, (a, b, c) = make_room(settings={"first": "host", "rounds": 1})
    room.start(a, 0)
    for _ in range(3):
        play_turn(room)
    assert room.phase == "ended"
    room.start(a, 0, {"rounds": 3, "time_limit": None, "first": "host"})
    assert room.phase == "playing" and all(not p.won for p in room.players)
    room.draw(a, 0)
    assert room.deadline is None


def test_join_rules():
    room, players = make_room()
    with pytest.raises(GameError):
        room.add_player("p0", ICON, 0)
    with pytest.raises(GameError):
        room.add_player("   ", ICON, 0)
    with pytest.raises(GameError):
        room.add_player("Zed", {"shape": 99, "color": "#ffd23f"}, 0)

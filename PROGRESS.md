# Katakanashi Online: Progress Tracker

This file tracks the project across Claude Code sessions. The game idea lives in `concept.md`.

## How to use this file

- **At the start of a session:** read this file and `concept.md`.
- **During a session:** add new feedback and decisions to the right section.
- **At the end of a session:** update "Status", tick off goals, refresh "Next up", and add one line to the session log.
- **Pruning:** once feedback is built in the real app and working, delete it. A rule that you can't easily see in the code, and that future work must keep following, moves to "Standing rules". Everything else goes.

## Status

**Phase:** Building. A first full version of the game is built and committed: create/join rooms, lobby, first-player wheel, turns, timer, host menu, end screen, and reconnecting. Two scripted browser runs pass (a normal 3-player game, and the tricky cases: endless mode, 8 players, someone leaving, removing players, joining by link, wrong room codes). It has **not** been played by real people yet, and it hasn't been pushed to GitHub yet.

**How to run:** `./dev.sh` starts both, then open http://localhost:5173. Backend tests: `cd backend && uv run pytest`.
- `frontend/`: Vue + Vite. In dev, Vite passes `/api` and `/ws` through to the backend.
- `backend/`: FastAPI, managed with `uv`. Code is in `backend/app/`, tests in `backend/tests/`.

Mockups live in `mockups/`:
- `c2-game-show.html`: **the current direction.** It's the game show mockup, revised with the feedback below. It has a "mockup controls" panel on the left for switching views and standee styles.
- `c-game-show.html`: the first version of the game show mockup, kept for comparison.
- `a-round-table.html`, `b-scoreboard.html`: options we didn't pick. A few parts from them are being reused.

## Roadmap

- [x] Write the concept (`concept.md`)
- [x] Make three UI mockups and pick one (picked C)
- [x] Revise mockup C with feedback (`c2-game-show.html`)
- [x] User reviews C2 and picks a standee style (picked Desk)
- [x] Set up the project: Vue (Vite) frontend and FastAPI backend, run together locally
- [x] Live connection: rooms that push updates to every player in real time (likely WebSockets)
- [x] Title screen: create a room or join one by code or link
- [x] Lobby: player list, host settings, how-to-play popup, Start button
- [x] Picking the first player: spinning wheel, or the host goes first
- [x] Core turn: draw, highlight the word, timer, hand the card over, next turn, round counter
- [x] What guessers see: the card held above the describer's standee, plus the timer
- [x] Deck and discard pile: missed cards go to the discard pile, which is shuffled back in when the deck runs out. If both are empty, the game ends
- [x] Host menu: table color, fix a mistake, end game (between rounds), close room
- [x] End screen: podium with the top 3, then Play again (same room, new settings) or Close room
- [x] Word list: a simple placeholder set for now, the real one later
- [ ] Custom player icons and UI icons, chosen when joining
- [ ] Put it online somewhere friends can reach

## Next up

1. Push to GitHub (waiting on the user's OK).
2. User playtests with friends and gives feedback.
3. Custom player and UI icons. Then decide on hosting.

## Feedback and decisions waiting to be built

Everything in this section is already shown in mockup C2 unless it says otherwise. It still needs building in the real app.

### Visual and UI
- **No emoji anywhere.** Custom icons will replace them later. Until then, use the simple placeholder faces from C2.
- **No em-dashes in UI text.** This includes word definitions in the data.
- **Standees:** use the **Desk** style from C2: short game-show desks in a curve, with light bulbs and a glowing score. (Mat and Rosette are still in C2's mockup controls, but we're not using them.)
- **Timer:**
  - The describer sees a bar right under their card.
  - Guessers see a big round timer in the middle of the screen.
  - Big pop-up warnings appear at 20 and 10 seconds.
  - The screen edges glow red in the last 5 seconds.
- **End screen:** a podium with confetti (idea from mockup A), restyled to match the game show look. "Play again" opens a settings panel in the same room.
- **How-to-play popup:** reuse the one from mockup B, with its reminder to join voice chat. *(Not in C2 yet.)*

### Gameplay rules
- **Refreshing or dropping out:** the browser remembers who the player is, so a refresh or reconnect puts them right back in their seat with their cards. While someone is gone, their turn is skipped. The host can remove a player from the host menu.
- **Only the describer sees the card's words.** Everyone else watches the card get drawn and held up above the describer's standee, back side facing out. Everyone sees the timer.
- **Highlighting the next card's number is only for the describer.** Guessers can see the number on the back of the next card, but it isn't highlighted for them.
- **Only the describer hands out the card.**
- **Host menu:** this is where the host can fix a mistake. Fixing takes several steps (pick who to take the card from, then who gets it, then confirm), so it can't be done with a quick single click. Everyone sees a note when the host moves a card.
- **When nobody guesses:** the card goes to a discard pile. When the deck runs out, the discard pile is shuffled to make a new deck.
- **Ending an endless game:** at the end of each round, the host is asked "Next round, or end game?". "End game" in the host menu only works between rounds. "Close room" in the host menu works at any time, after a confirmation.
- **Cards have categories, but they're hidden.** Every card's 6 words share a theme, like food, office supplies, or flavors. Some themes and words are pretty obscure. The category is never shown on the cards or anywhere in the UI. It can live in the data, but it never reaches the screen.

## Open questions

- **Real word list:** the user owns the physical card game, but copying the words out of it could be a chore. For now, use a small made-up set and come back to this later.
- **Hosting:** where will it run online? (Decide later. SQLite is fine for now.)

## Standing rules

These stay true for the whole project.

- Style: flat, bright colors, bold dark outlines, 2D table and decks, 3D card movement. Cartoon shapes in the background. Each room gets one of about 10 bright but soft table colors.
- The server keeps the real deck order secret. A player's browser should never get card words it isn't supposed to see.
- Small project, just for friends. Pick simple over scalable.
- **The server is the referee.** It holds the deck, the turn order, and the timer. Browsers only send requests ("I drew", "give the card to X"). The server checks them and tells everyone the result.
- **Each player gets their own view.** The server builds what each player sees, so only the describer ever receives the card's words.
- Rooms live in the server's memory for now. Add SQLite only when we need it.

## Session log

- **2026-10-05:** Made mockups A (Round Table), B (Scoreboard), and C (Game Show). The user picked C and gave feedback. Started this tracker. Then made C2 with that feedback, including three standee styles to choose from.
- **2026-10-05:** User reviewed C2 and picked the Desk standee. Decided the category is hidden everywhere (removed it from C2's card), and the game ends if the deck and discard pile both run out (rare, since there will be lots of cards).
- **2026-10-05:** Decided how players stay connected and how reconnecting works. Set up the Vue + FastAPI project with a run-both script, a health check, and a WebSocket ping test.
- **2026-10-05/06:** Built the backend (rooms, game rules, live updates, reconnecting, placeholder words) with 31 passing tests, and committed it. Built the whole frontend from the C2 mockup. A scripted 3-player browser run went through the full game; fixed a few small bugs it found ("Waiting for undefined", a leftover warning dot, lobby layout, table showing behind the end screen). Session cut off before the second browser test and before committing the frontend.
- **2026-10-06:** Ran the second browser test (tricky cases). All checks passed. Fixed three small things it showed: an empty timer circle when there's no time limit (now hidden), the host being told "Waiting for the host" between rounds, and players with 0 cards standing on the podium. Committed the frontend.

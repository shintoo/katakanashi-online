# Katakanashi flavor text

Edit the text after each `→` arrow, then hand this file back. I'll put your changes into the game.

- **To change a line:** rewrite the text after the `→`.
- **To leave a line alone:** don't touch it.
- **To leave a note instead:** add `// your note` at the end of the line (for example `// make this funnier`).
- **`{name}`-style parts** get filled in by the game. Keep them, or move them around in the sentence.
- **ALL CAPS lines** are written in caps in the code. If you write them in normal case, I'll keep the caps for you.

Plain labels like "Back", "Cancel", "Join", "Rounds" and "Copy link" are left out.

---

## Title screen

| ID | Where it shows up | Text |
|---|---|---|
| T1 | "Host a game" card | → Make a new room and invite your friends with a code or a link. |
| T2 | "Join a game" card | → Got a room code from a friend? Type it here. |
| T3 | Heading on the form when you create a room | → Who's hosting? |
| T4 | Heading on the form when you join by link | → Join room {code} |
| T5 | Banner after the host removes you | → Oh no, you've been kicked! |
| T6 | Banner after the room closes | → This room is closed. Thanks for playing! |
| T7 | Phone held upright | → Turn your phone sideways! |
| T8 | While loading a room | → Connecting... |
| T9 | When the connection drops | → Reconnecting... |

## How to play popup

| ID | Where it shows up | Text |
|---|---|---|
| H1 | Step 1 heading | → 1. 引く! |
| H2 | Step 1 text | → Draw a card. Your word will light up. |
| H3 | Step 2 heading | → 2. セツメイ! |
| H4 | Step 2 text | → Explain it without saying *any* katakana words. |
| H5 | Step 3 heading | → 3. 推測! |
| H6 | Step 3 text | → First to guess it wins the card |
| H7 | Voice call line | → (This game has no voice chat - use Discord or something) |
| H8 | Close button | → 分かった、イコー! |

## Lobby

| ID | Where it shows up | Text |
|---|---|---|
| L1 | Empty player slot | → Waiting for friends to join... |
| L2 | Under Start, with only 1 player | → You need at least 2 players. |
| L3 | What non-hosts see instead of Start | → Waiting for {host} to start the game |
| L4 | Start button | → スタート! |

## Who goes first (the wheel)

| ID | Where it shows up | Text |
|---|---|---|
| W1 | Heading | → サイショは誰? |
| W2 | Middle of the wheel | → GO |
| W3 | Non-hosts, before the spin | → Waiting for the host to spin... |
| W4 | Result, if it's you | → You draw first! |
| W5 | Result, if it's someone else | → {name} draws first! |
| W6 | Spin button | → SPIN! |
| W7 | Start button after the spin | → スタート! |
| W8 | Big pop-up word, if it's you | → YOU FIRST! |
| W9 | Big pop-up word, someone else | → {NAME} FIRST! |

## During a turn: the describer's screen

| ID | Where it shows up | Text |
|---|---|---|
| D1 | Over the deck when it's your turn | → Your turn: 引いて! |
| D2 | Empty card spot | → your card goes here |
| D3 | Sticky note, front heading | → 分からない? |
| D4 | Sticky note, front small text | → 意味を表示 |
| D5 | Pink rule sign | → カタカナ禁止! |
| D6 | Pass button | → 諦める |
| D7 | Over a player's desk when you can hand them the card | → 与える |

## During a turn: what guessers see

| ID | Where it shows up | Text |
|---|---|---|
| G1 | Over the deck | → {name}のバン |
| G2 | Big title, before the draw | → {NAME} IS ABOUT TO DRAW |
| G3 | Small text, before the draw | → 準備はイイ？ |
| G4 | Small text, if the describer dropped out | → Waiting for {name} to come back... |
| G5 | Big title, while describing | → {NAME}のセツメイを聞いて |
| G6 | Small text, while describing | → 推測して！ |

## Pop-up words (big text that flies across the screen)

| ID | When | Text |
|---|---|---|
| P1 | Someone gets a card (one of these three, picked at random) | → セイカイ! |
| P2 | (same) | → 頭イイね! |
| P3 | (same) | → スゴイ!!1! |
| P4 | Discard pile shuffled into the deck | → SHUFFLE! |
| P5 | New round starts | → ラウンド {n}! |

## Notices (small messages at the bottom of the screen)

| ID | When | Text |
|---|---|---|
| N1 | Nobody guessed it | → みんなシッパイ・・・ The card goes to the discard pile. |
| N2 | Discard pile shuffled back in | → The discard pile was shuffled back into the deck. |
| N3 | Host fixed a mistake | → The host moved a card from {from} to {to}. |
| N4 | Someone joined | → {name}がトウジョウ. |
| N5 | Someone was removed | → {name}はキックされた！ |
| N6 | Someone's turn was skipped | → {name} is away, so their turn was skipped. |
| N7 | Host left, and you're the new host | → The host left, so you are the host now. |
| N8 | Host left, someone else is the new host | → The host left, so {name} is the host now. |

## End of a round

| ID | Where it shows up | Text |
|---|---|---|
| R1 | Big title | → ラウンド{n}終了! |
| R2 | Host's text | → You're the host. Keep going, or end the game? |
| R3 | Everyone else's text | → Waiting for the host to start the next round |
| R4 | Guesser's big title (behind the box) | → ROUND OVER |
| R5 | Guesser's small text, if host | → Next round, or end game? |
| R6 | Guesser's small text, not host | → Waiting for the host |

## End of the game

| ID | Where it shows up | Text |
|---|---|---|
| E1 | Title | → FINAL SCORES |
| E2 | Title, when everyone tied | → IT'S A TIE! |
| E3 | Under the tie title | → {n cards} each. Everybody wins! |
| E4 | Under the tie title, when nobody scored | → Nobody got a single card. Wow. Everybody wins anyway! |
| E5 | Tag on a podium step, everyone tied | → ALL TIED! |
| E6 | Tag on a podium step, some tied | → TIE! |
| E7 | Non-hosts' text | → Waiting for the host to start a new game |
| E8 | "Play again" heading | → New game, same room |
| E9 | "Play again" text | → Pick your settings. Everyone stays in the room. |
| E10 | "Close the room?" text | → This sends everyone back to the title screen. |

## Host menu

| ID | Where it shows up | Text |
|---|---|---|
| M1 | "Fix a mistake" small text | → Move a card that went to the wrong player |
| M2 | "Remove a player" small text | → For someone who left for good |
| M3 | "End game" small text | → Show the final scores now |
| M4 | "End game" small text, mid-round | → Available between rounds |
| M5 | "Close room" small text | → Ends the game for everyone |
| M6 | "Fix a mistake" popup text | → Move one card from one player to another. Everyone will see a note that the host moved a card. |
| M7 | "Remove a player" popup text | → Their cards go to the discard pile. They can join again with the room code. |
| M8 | "Close the room?" popup text | → This ends the game for everyone and sends them back to the title screen. |
| M9 | "Close the room?" keep button | → Keep playing |

## Error messages

Most of these only show up if something odd happens. The ones players are likely to see are marked ★.

| ID | When | Text |
|---|---|---|
| X1 ★ | Wrong room code | → There's no room with that code. |
| X2 ★ | Room has 10 players | → This room is full. |
| X3 ★ | Name already taken | → Someone in this room already has that name. |
| X4 ★ | Name left blank | → Please enter a name. |
| X5 | Name too long | → Names can be up to {max} letters. |
| X6 | Something broke while talking to the server | → Something went wrong. Try again? (or ask Sean) |
| X7 | Not your turn | → It's not your turn. |
| X8 | Tried to give a card before drawing | → Draw a card first. |
| X9 | Tried to draw twice | → You already have a card. |
| X10 | Non-host tried a host action | → Only the host can do that. |
| X11 | Started with 1 player | → You need at least 2 players. |
| X12 | Host-menu card move with no cards | → {name} has no cards to move. |

# Katakanashi Online

## Background

Katakanashi is a Japanese word game. A group of 3 or more players typically plays it, but it can be played with two.
The players sit in a circle, with a pile of cards in the middle of the table.
Each card has a number, 1-6, on the back.
On the front of the cards are 6 words in a list.
Every word on the front of the card is a Katakana Japanese word.
When it is a player's turn, they draw one card, and look at the words on the front of the card.
The *next* card in the deck, that is now the top card, indicates which word the player should choose.

For example, if player A draws the top card, then the *new* top card of the deck has the number 3 on the back,
then player A will choose word #3 on the front of their card.

The player does not show others the card. They must describe the word to the other players, in Japanese,
without using any Katakana words themselves. The first player to correctly guess the word wins the card, which
serves as a point.
Then, the next person in the circle (clockwise or counterclockwise, either works) draws the top card from the deck.
This continues until either all of the cards are exhausted, or until a pre-determined number of rounds are completed.

## Online concept

Katakanashi Online is a web-based version of this game. Players will use their own voice chat platforms (such as Discord)
to interact. The typical flow will work like this:

The host goes to the website, selects "Create a room", and is given a unique room code once their room is created.
(They can also be given a link that has their room code embedded, for them to share).
The host can select whether to randomize the first player, whether to set a time limit per card (30s, 1m, 2m, 5m, or no limit),
and the total number of rounds (or endless).
Then, they invite the other players to the room using the link or room code. If sharing a room code, the other players
can go to the website and enter the room code.
Upon joining the room, a brief "how to play" (in English) is shown - it also notes that they
should be in a voice chat with the other players.
Once the players are in the room, the host can select "start game".
An animation plays that indicates which player is drawing first - it is randomized, and spins like a wheel.
Or - the host can elect to go first themselves (this is helpful for when only the host has played the game before).
The host can choose whether to go first or to randomize the first player when creating the room.

The deck of cards is shown in the middle of the screen. When it is a player's turn, they can click the top of the
deck, and the card will be drawn and shown to them - the new top card of the deck will have its number highlighted,
and the corresponding word on the card will be highlighted as well. Also on the UI, the definition (in english)
will be shown to the user, in case they don't know the word.
If the host selected timed rounds when creating the room, the timer will begin.
Then, as the player describes the selected word, the other players guess, using their voice chat.
Whoever guesses the word correctly gets the card, and the player giving the description will give their
card to them by clicking on that player's icon, or play area, or some other UI indicator.
When the guesser receives the card, it is added to their pile, which indicates how many cards they have won.

When the round ends, after all players have been given a chance to draw a card and describe a word, the round counter
increments. That's all that happens if there is no round limit set. If it's the final round, the scores are tallied
and the winner (or top 3 winners?) are presented in an entertaining way.

The host will then be offered a "play again" dialog, and be able to select any new room configurations, like the round limit,
whether to randomize the first player, and the time limit per card. When they select play again, it will reuse the same room.
They can also select to close the room.

## Design

The design of the game will be flat, with bright colors, and bold outlines. The graphics will be 2D, but with 3D card effects,
such as when drawing and moving cards. The decks themselves will be 2D, as is the table. It will use cartoony shapes and colors
on the background, such as yellow triangles, purple squiggles, and so on. The background (the table) will have a different color depending on the room - it can select from one of perhaps 10 preset colors. They should be bright, but not harsh.

## Tech stack

The UI will be implemented in Vue. The backend will be implemented in Python using FastAPI. It will use an sqlite database at first. When this goes online for real, we may migrate to online-first services (think Firebase, or anything like that. Open to suggestions when we get to this point).

## Notes

This game will almost entirely only be played between me and a few of my friends. It does not need to be scalable. Just for fun!

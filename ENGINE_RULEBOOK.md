# ENGINE_RULEBOOK.md

Project: Gaple Engine

Document: ENGINE_RULEBOOK.md

Version: 1.0

Status: Draft

Last Updated: 2026-06-30

---

# Gaple Engine Rulebook

This document defines the official gameplay rules implemented by the Gaple Engine.

Whenever the implementation differs from this document, this document is considered the authoritative source.

Implementation details are documented separately in ENGINE_ARCHITECTURE.md.

---

# Part 1 - Game Fundamentals

## 1. Scope

This rulebook defines the official gameplay rules used by the Gaple Engine.

It describes only the rules of the game.

Software architecture and implementation details are intentionally excluded from this document.

---

## 2. Terminology

This rulebook preserves the original terminology used in the local Gaple rules.

The following terms are official project terminology and are intentionally not translated.

- Balak
- Dom
- Pasar
- Guplah
- Ratus
- Ribu
- Mati

Whenever these terms appear in this document, they must be interpreted according to the definitions provided here.

International domino terminology must never replace these official terms.

---

## 3. Equipment

The game uses one standard Double-Six domino set consisting of twenty-eight unique dominoes.

Each domino contains two values.

The values range from 0 to 6.

Examples:

- 6-6
- 6-5
- 4-2
- 1-0

Each domino exists exactly once.

Duplicate dominoes are not allowed.

---

## 4. Players

The game is played by exactly four players.

The game does not use permanent teams.

Every player competes individually.

---

## 5. Objective

The objective of the game is to complete a game according to the official rules defined in this rulebook.

A game may end through one of the official ending conditions:

- Dom
- Pasar
- Guplah
- Ratus
- Ribu

Some ending conditions determine a winner immediately, while others require additional evaluation.

---

## 6. Definitions

### Domino

A domino is one tile containing two values.

Examples:

- 6-4
- 5-0
- 3-3

Domino orientation has no meaning.

For example:

6-4 and 4-6 represent the same domino.

---

### Double (Balak)

A Double (Balak) is a domino whose two values are identical.

Examples:

- 0-0
- 1-1
- 2-2
- 3-3
- 4-4
- 5-5
- 6-6

Some ending conditions require one or more Double dominoes.

---

### Table Ends

The table always has two playable ends.

- Left End
- Right End

A legal move must connect to one of these ends unless it is the opening move.

---

### Dead (Mati)

A player is considered Dead (Mati) if, during their turn, they have no legal move on either end of the table.

A Dead player must Pass.

Example:

Table ends:

0 .... 3

If a player owns no domino containing either 0 or 3, that player is Dead.

---

### Closed Cycle

A Closed Cycle occurs when the domino chain forms a complete loop.

Examples:

2-3 → 3-4 → 4-2

or

2-3 → 3-4 → 4-2 → 2-1 → 1-0

When a Closed Cycle is formed:

- The completed cycle is closed.
- The closed section is no longer playable.
- The remaining open chain continues the game.

Closed dominoes are no longer visible during gameplay but are still considered played.

Players are expected to remember every domino that has been played.

---

## 7. Game Setup

The complete domino set is shuffled.

Each player receives seven dominoes.

All twenty-eight dominoes are dealt.

No domino remains outside the game.

---

## 8. Opening Rules

### First Game

The player holding Double Six (6-6) starts the first game.

The opening move must be Double Six.

No other opening move is allowed.

---

### Later Games

The opening player depends on the result of the previous game.

The rules governing later openings are defined in Part 4 of this rulebook.

The Game itself does not determine who opens the next game.

---

# Part 2 - Gameplay

## 9. Legal Moves

During a player's turn, the player must perform exactly one of the following actions:

- Play one domino.
- Play multiple dominoes in a single move.
- Pass.

A move is legal only if every domino played can be connected to the current table according to the official game rules.

If no legal move exists, the player must Pass.

---

## 10. Single Domino Move

A player may play one domino if it can be legally connected to either open end of the table.

If both ends are valid, the player may freely choose either side.

Example:

Table:

6 .... 3

Hand:

3-6

The domino may be played on either the left end or the right end.

---

## 11. Multiple Domino Move

A player may play two or three dominoes during a single turn.

A multiple domino move is legal only if:

- Every domino is played in a valid sequence.
- Every intermediate table position remains legal.
- The complete sequence is performed without interruption.

The engine evaluates only the legality of the move.

The engine does not determine whether the move is a successful Ratus or Ribu during gameplay.

Those evaluations are performed only after the game has ended.

---

## 12. Player Turn

Each player's turn follows this sequence:

1. The active player begins their turn.
2. The player selects a legal move.
3. If no legal move exists, the player must Pass.
4. The selected move is applied to the table.
5. Closed Cycle detection is performed.
6. End-of-game conditions are evaluated.
7. If the game continues, the next player's turn begins.

---

## 13. Passing

Passing is mandatory whenever a player has no legal move.

Passing is not allowed if at least one legal move exists.

Passing does not change the player's hand.

The turn immediately ends after a Pass.

---

## 14. Closed Cycle Handling

After every successful move, the table is checked for a Closed Cycle.

If a Closed Cycle is formed:

- The completed cycle is closed.
- The closed section is removed from further play.
- The remaining open chain continues as the active table.

Closed dominoes remain part of the game history and are considered played.

---

## 15. End of Turn

A turn ends immediately after:

- A legal move has been completed, or
- The player Passes.

After the turn ends, the engine evaluates whether the game should continue or end.

If the game continues, the next player becomes the active player.

---

# Part 3 - Ending Conditions

## 16. General Principles

The game ends immediately when one of the official ending conditions is satisfied.

Ending conditions are evaluated only after a move has been completely executed.

The engine never informs a player whether a move is considered Dom, Pasar, Guplah, Ratus, or Ribu before the game ends.

The engine evaluates only the legality of moves during gameplay.

---

## 17. Dom

Dom occurs when a player successfully plays their final domino.

Dom always succeeds.

The game immediately ends.

The winner is the player who played the final domino.

---

## 18. Pasar

Pasar occurs when a player's final domino can legally be played on both open ends of the table.

The player may choose either side.

Pasar always succeeds.

The game immediately ends.

The winner is the player who played the final domino.

---

## 19. Guplah

Guplah may occur when a move causes both open ends of the table to show the same value.

After the move, the engine evaluates whether every domino containing that value has been played.

If at least one domino containing that value still remains in another player's hand, Guplah does not occur and the game continues.

If no such domino remains, the game immediately ends.

All remaining players reveal their dominoes.

The player with the lowest total pip count is declared the winner.

---

### Failed Guplah

If the player attempting Guplah is not the player with the lowest total pip count, the Guplah attempt fails.

No winner is declared.

Only the player who attempted Guplah receives the official Guplah penalty.

---

## 20. Ratus

Ratus is an ending condition created by playing exactly two dominoes during a single move.

The move itself is evaluated only after the game has ended.

The engine does not determine whether a move is Ratus during gameplay.

A successful Ratus requires:

- The final move contains exactly two dominoes.
- One domino is a Balak.
- The move satisfies the official Ratus rules.

If all requirements are satisfied, the game immediately ends.

The player is declared the winner.

---

### Failed Ratus

If the move does not satisfy the official Ratus requirements after evaluation:

- No winner is declared.
- The player who attempted Ratus receives the official Ratus penalty.

---

## 21. Ribu

Ribu is an ending condition created by playing exactly three dominoes during a single move.

The move itself is evaluated only after the game has ended.

The engine does not determine whether a move is Ribu during gameplay.

A successful Ribu requires:

- The final move contains exactly three dominoes.
- Two dominoes are Balak.
- The move satisfies the official Ribu rules.

If all requirements are satisfied, the game immediately ends.

The player is declared the winner.

---

### Failed Ribu

If the move does not satisfy the official Ribu requirements after evaluation:

- No winner is declared.
- The player who attempted Ribu receives the official Ribu penalty.

---

# Part 4 - Post-Game Rules

## 22. Game End

A game ends immediately after one of the official game outcomes has been evaluated.

The official game outcomes are:

- Dom
- Pasar
- Guplah
- Ratus
- Failed Ratus
- Ribu
- Failed Ribu

Once a game has ended:

- No additional moves may be played.
- The official outcome is recorded.
- The winner is determined according to the outcome.
- The opening rule for the next game is determined.

---

## 23. Determining the Winner

Each official game outcome determines the winner differently.

### Dom

The player who plays the final domino is the winner.

---

### Pasar

The player who plays the final domino is the winner.

---

### Guplah

After Guplah occurs, every remaining player reveals their dominoes.

The total pip value of each remaining hand is calculated.

The player with the lowest total pip value is declared the winner.

The player who creates the Guplah is not automatically the winner.

---

### Ratus

The player who performs the Ratus is declared the winner only if the official Ratus evaluation succeeds.

---

### Failed Ratus

No winner is declared.

---

### Ribu

The player who performs the Ribu is declared the winner only if the official Ribu evaluation succeeds.

---

### Failed Ribu

No winner is declared.

---

## 24. Opening the Next Game

The opening player of the next game depends on the official outcome of the previous game.

### After Dom

The winner opens the next game.

The opening move is unrestricted.

---

### After Pasar

The winner opens the next game.

The opening move is unrestricted.

---

### After Guplah

The owner of the Balak corresponding to the Guplah value opens the next game.

The opening move must be that Balak.

---

### After Ratus

The next game follows the default opening procedure.

---

### After Failed Ratus

The next game follows the default opening procedure.

---

### After Ribu

The next game follows the default opening procedure.

---

### After Failed Ribu

The next game follows the default opening procedure.

---

## 25. Match System

A single Game produces only an official game outcome.

Penalty calculation, cumulative scoring, and match completion are defined separately by the Match System.

The Match System uses the official game outcome produced by the Game.

---

## 26. Local Rule Priority

This engine implements the official local Gaple rules documented by this project.

Whenever a conflict exists between this rulebook and international domino rules, this rulebook always takes priority.

International domino behavior must never replace the rules defined in this document.

---

## End of Rulebook

This document defines the official gameplay rules implemented by the Gaple Engine.

Software architecture and implementation details are documented separately.

Any future gameplay additions must remain consistent with this rulebook.
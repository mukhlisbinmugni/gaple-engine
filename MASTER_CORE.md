# MASTER_CORE.md

Version: 4.7

Status: Active

Last Updated: 2026-07-03

---

# Gaple Engine Master Core

## Purpose

This document defines the permanent philosophy, architecture, and design principles of the Gaple Engine project.

All AI assistants must read and follow this document before implementing, modifying, or reviewing any part of the project.

Whenever an implementation conflicts with this document, this document is the single source of truth.

---

# Project Vision

Gaple Engine is an open-source Python engine implementing the local Gaple rules used in Kalimantan.

This project is **NOT** an implementation of international domino rules.

The engine is intended to become the foundation for:

- AI research
- Match simulation
- Strategy analysis
- REST API
- Mobile applications
- Web applications

The engine contains no user interface.

---

# Engine Philosophy

The engine executes the game.

The engine never teaches strategy.

The engine never evaluates whether a move is good or bad.

The engine simply enforces the rulebook.

Gaple is modeled using the local Kalimantan rulebook rather than international domino rules.

---

# Separation of Responsibilities

## Models

Models store data only.

Examples:

- Domino
- Move
- Player
- TurnResult
- GameEndResult

Models never execute game rules.

---

## Logic

Logic classes execute game rules.

Examples:

- Deck
- Table
- MoveGenerator
- Game
- RuleSystem
- Match

Each class must have exactly one responsibility.

---

# Three-Layer Architecture

## Layer 1 — Game

Game is responsible only for gameplay.

Responsibilities:

- turn order
- legal move validation
- player rotation
- table state
- pass counting
- detecting that gameplay has finished

Game never determines:

- DOM
- PASAR
- GUPLAH
- RATUS
- RIBU

Game records only factual game state.

---

## Layer 2 — RuleSystem

RuleSystem interprets a finished Game.

RuleSystem determines:

- winner
- finish strategy
- special result
- penalty changes

RuleSystem never modifies gameplay.

---

## Layer 3 — Match

Match manages multiple Game instances.

Responsibilities:

- creating Game objects
- selecting opening players
- carrying GameEndResult
- match progression

---

# Move Philosophy

Move represents only a physical move.

Move stores:

- a list of Placements (one Placement per domino actually placed
  within this Move)
- move type

Each Placement stores exactly one domino and the side it was aimed
at. A Move with one Placement is NORMAL. A Move with two Placements
is RATUS. A Move with three Placements is RIBU.

Move never determines:

- DOM
- PASAR
- GUPLAH
- RATUS
- RIBU

Move is atomic: Table applies every Placement within a Move in
order, but if any single Placement fails, the entire Move is rolled
back as if it never happened. A Move can never leave the table in a
partially-applied state.

---

# Finish Philosophy

Game determines only that gameplay has finished.

RuleSystem determines **how** the game finished.

---

# Winning Strategy Philosophy

Gaple can finish using five different winning strategies.

These strategies are considered equally valid.

The engine never prioritizes one strategy over another.

The five finish strategies are:

- DOM
- PASAR
- GUPLAH
- RATUS
- RIBU

Each strategy defines its own:

- detection rule
- winner rule
- penalty rule

---

# DOM Philosophy

DOM occurs when a player legally plays their final domino and empties their hand.

Winner:

The player who empties their hand.

Penalty:

The DOM penalty is assigned to the player carrying the largest remaining burden.

The penalty recipient is determined using the following priority.

**Each tie-break step evaluates only the players who remain tied from the previous step. Players eliminated by an earlier step are never reconsidered during later steps.**

## Step 1 — Largest Remaining Pip Total

Find the player with the largest total remaining pip count.

If only one player has the largest total, that player receives the penalty.

Otherwise, continue to Step 2 using only the tied players.

---

## Step 2 — Greatest Number of Remaining Dominoes

Among the remaining tied players, compare the number of dominoes still held.

If only one player holds the greatest number of remaining dominoes, that player receives the penalty.

Otherwise, continue to Step 3 using only the tied players.

---

## Step 3 — Double Domino (Balak)

Evaluate only the players who remain tied after Step 2.

### Step 3.0 — Presence of Balak

If none of the tied players holds a double domino (balak), skip Step 3 entirely and continue to Step 4 using all remaining tied players.

If exactly one tied player holds one or more double dominoes, that player receives the penalty. This comparison is decided immediately and does not proceed to Step 3a, Step 3b, or Step 4.

If two or more tied players each hold one or more double dominoes, eliminate every tied player who holds no double domino, and continue to Step 3a using only the remaining balak-holding players.

### Step 3a — Number of Balak Held

Among the remaining balak-holding players, compare how many double dominoes each of them holds.

If only one player holds the greatest number of double dominoes, that player receives the penalty.

Otherwise, continue to Step 3b using only the players who are still tied on balak count.

### Step 3b — Highest Balak Value

Among the players still tied after Step 3a, compare the pip value of each player's own highest double domino (for example, 5-5 has a balak value of 10, 3-3 has a balak value of 6).

This comparison uses only the value of the double dominoes themselves. Non-double dominoes held by these players are not considered at this step, even though every player being compared already has an identical total pip count from Step 1.

The player holding the highest-valued double domino receives the penalty.

Because a standard double-six set contains exactly one domino of each value, no two players can hold a double domino of the same value. Step 3b therefore always produces exactly one penalty recipient once it is reached.

Step 4 is never reached when Step 3a or Step 3b resolves the tie.

### Examples

**Example 1 — Exactly one balak holder (Step 3.0)**

P1: 3-2, 5-5 → Total Pip = 15

P2: 4-1, 6-4 → Total Pip = 15

P3: 1-1 → Total Pip = 2

Winner: P4

Only P1 and P2 remain tied after Step 1. P3 is no longer considered.

Since only P1 holds a double domino, P1 receives the penalty.

**Example 2 — Multiple balak holders, resolved by balak count (Step 3a)**

P1: 5-5, 1-1, 1-0 → Total Pip = 13, 3 dominoes, holds 2 balak (highest balak value = 5-5)

P2: 4-4, 2-0, 3-0 → Total Pip = 13, 3 dominoes, holds 1 balak (highest balak value = 4-4)

P1 and P2 are tied after Step 1 and Step 2. Both hold at least one balak, so all non-balak-holding tied players are eliminated, and Step 3a is evaluated.

P1 holds 2 double dominoes, P2 holds 1 double domino.

P1 receives the penalty.

**Example 3 — Multiple balak holders, tied balak count, resolved by balak value (Step 3b)**

P1: 5-5, 1-1, 1-0 → Total Pip = 13, 3 dominoes, holds 2 balak (highest balak value = 5-5, pip 10)

P2: 4-4, 2-2, 1-0 → Total Pip = 13, 3 dominoes, holds 2 balak (highest balak value = 4-4, pip 8)

P1 and P2 are tied after Step 1 and Step 2, and both hold exactly 2 balak, so Step 3a does not resolve the tie.

Step 3b compares each player's highest balak value: P1's highest balak (5-5, pip 10) is greater than P2's highest balak (4-4, pip 8).

P1 receives the penalty.

---

## Step 4 — Highest Remaining Domino

Evaluate only the players who reach this step, meaning either:

- no tied player at Step 3 held a double domino, or
- exactly one tied player remains after all earlier steps for a reason other than balak (this step is the final fallback).

For each remaining player, identify their own highest-ranked domino using the following order:

1. The domino with the greatest pip sum (the two sides added together).
2. If two or more of the player's own dominoes share the same pip sum, the one with the higher single value.
3. If still equal, the one with the lower single value.

Once each player's highest-ranked domino has been identified, compare those dominoes across players using the same order:

1. Compare the pip sum.
2. If equal, compare the higher single value.
3. If still equal, compare the lower single value.

The player holding the higher-ranked domino receives the penalty.

**Example 1**

P1: 6-1, 4-0 → Highest domino by pip sum = 6-1 (pip sum 7)

P2: 6-2, 3-0 → Highest domino by pip sum = 6-2 (pip sum 8)

Both players have:

- identical total pip
- identical number of dominoes
- no double domino

Therefore Step 4 is applied.

Because 6-2 has a pip sum of 8 and 6-1 has a pip sum of 7, and 8 > 7, P2 receives the penalty.

Because every domino in a standard double-six set is unique, and each domino being compared belongs to a different player, this comparison always produces exactly one penalty recipient.

---

# PASAR Philosophy

PASAR is a special form of DOM.

A player finishes the game by legally playing their final domino.

The final domino must be legally playable on both open ends of the table simultaneously.

PASS is not required.

Other players may still have legal moves.

PASAR depends only on the legality of the final move.

Winner determination follows the DOM winner rule.

Penalty:

Penalty determination follows the exact same tie-break sequence as
DOM (Step 1 through Step 4, including the balak sub-steps 3a and
3b). The only difference between DOM and PASAR is the magnitude of
the penalty:

- DOM: the winner receives -3, the penalty recipient receives +3.
- PASAR: the winner receives -4, the penalty recipient receives +4.

This reflects the local Kalimantan rule that PASAR is a stronger
finish than DOM: DOM only requires emptying the hand, while PASAR
requires the final domino to be legally playable on both open ends
of the table at once. The greater difficulty is rewarded with a
greater penalty swing.

---

# GUPLAH Philosophy

GUPLAH occurs when gameplay becomes blocked and no further legal moves are possible for any player (a full round where every player PASSes).

The player who causes the block is not automatically the winner.

All remaining dominoes are revealed.

## GUPLAH Maker

The GUPLAH maker is the player who last successfully played a domino before the run of PASSes that led to the block. This is a factual identity, not an interpretation: Game records who played the last move.

## Winner

Step 1 — Smallest Remaining Pip Total

Find the player with the smallest total remaining pip count.

If only one player has the smallest total, that player wins.

Otherwise, continue to the GUPLAH Maker Override using only the tied players.

GUPLAH Maker Override

If the GUPLAH maker is one of the players tied for the smallest pip total, the GUPLAH maker wins immediately. No further step is evaluated.

If the GUPLAH maker is not one of the tied players (their pip total was not the smallest), continue to Step 2 using only the tied players, exactly as if the GUPLAH maker did not exist.

Step 2 — Fewest Remaining Dominoes

Among the remaining tied players, compare the number of dominoes still held.

The player holding the fewest remaining dominoes wins.

This is the opposite direction from DOM Step 2, because DOM Step 2 identifies the heaviest burden (a penalty recipient), while GUPLAH Step 2 identifies the winner.

If multiple players remain tied, continue to Step 3.

Step 3 — Double Domino (Balak)

Evaluate only the players who remain tied after Step 2.

If no tied player holds a double domino, skip Step 3 entirely and continue to Step 4 using all remaining tied players.

If exactly one tied player holds no double domino (is "clean"), that player wins immediately. This does not proceed to Step 3a, Step 3b, or Step 4.

If two or more tied players are clean (hold no double domino), eliminate every tied player who holds one or more double dominoes, then continue directly to Step 4 using only the clean players. There is nothing left to compare at the balak level among clean players, so Step 3a and Step 3b are skipped in this case.

If every tied player holds at least one double domino (no one is clean), resolve the tie among all of them as follows:

- Step 3a: compare how many double dominoes each of them holds. The player holding the fewest double dominoes wins.
- Step 3b: if the number of double dominoes held is also tied, compare the pip value of each player's own highest double domino. The player holding the lowest such value wins.

Both Step 3a and Step 3b use the opposite direction from DOM's equivalent sub-steps, because DOM looks for the heaviest balak burden while GUPLAH looks for the lightest one.

Step 4 is never reached when Step 3a or Step 3b resolves the tie.

Step 4 — Highest Remaining Domino, Lowest Value

Evaluate only the players who reach this step.

For each remaining player, identify their own highest-ranked domino using the same pip-sum-based method as DOM Step 4 (pip sum first, then higher single value, then lower single value).

Compare those dominoes across players using the same order, but the player whose highest domino has the LOWEST rank wins — the opposite direction from DOM Step 4.

## Penalty

The winner always receives -5.

The remaining penalty depends on whether the GUPLAH maker is the winner:

- If the GUPLAH maker is the winner: every other player receives +5 each.
- If the GUPLAH maker is not the winner: only the GUPLAH maker receives +5. Every other player who is neither the winner nor the GUPLAH maker receives 0 and is not penalized at all.

This reflects the local Kalimantan rule that GUPLAH penalizes the act of causing the block specifically, not simply "everyone who did not win," except in the case where the maker of the block also happens to hold the smallest pip total.

## Relationship to SpecialResult

`FinishType.GUPLAH` and `SpecialResult` answer two different questions and are always both present together when GUPLAH occurs:

- `FinishType.GUPLAH` answers "how did the game end" — it is a finish strategy, equal in standing to DOM and PASAR.
- `SpecialResult` answers "did the GUPLAH maker succeed" — it does not replace or compete with `FinishType.GUPLAH`.

Specifically:

- If the GUPLAH maker is the winner: `special_result = SpecialResult.GUPLAH`.
- If the GUPLAH maker is not the winner: `special_result = SpecialResult.FAILED_GUPLAH`.

For every other finish type (NORMAL), `special_result` remains `SpecialResult.NONE`.

---

# RATUS Philosophy

RATUS is an optional strategic move, not an automatic outcome and
not a required move. A player who satisfies RATUS's conditions is
never obligated to play it; they may choose to play NORMAL instead.

## Trigger

RATUS is attempted whenever a player, on their turn, plays their
last two remaining dominoes together as a single Move (a Move with
exactly two Placements, `MoveType.RATUS`). This is purely an action:
holding a qualifying pair of dominoes in hand does NOT constitute
RATUS by itself. RATUS only exists once the Move has actually been
played.

MoveGenerator does not require any particular shape for the two
dominoes (no "must be a double plus a connector" requirement at
generation time). It only checks that the two dominoes can be
legally connected to the table in some order and side assignment.
Whether the attempt succeeds or fails is determined afterward by
RuleSystem, not by MoveGenerator. MoveGenerator's job is to report
every legal way the two dominoes could be played, including
combinations that are legal to place but will not result in success
— the player (or AI) chooses which one to play, and a wrong choice
is a real, playable strategic mistake, not something the engine
prevents.

A Move is atomic: if the first Placement of a RATUS Move succeeds
but the second fails, the entire Move is illegal and rejected — it
cannot be attempted at all. There is no partial RATUS.

## Success and Failure

After a RATUS Move is played and the maker's hand is empty, success
is determined by two conditions, checked in order:

1. **Shape**: after the Move, both ends of the table must be equal
   to the same value. If the two ends differ, RATUS fails
   immediately — this is a failure of shape, regardless of what
   remains in other players' hands.
2. **Exhaustion**: if the shape is correct, every domino bearing
   that value must no longer exist in any other player's hand (all
   7 dominoes of that value must already be accounted for, either on
   the table or in the maker's now-empty hand).

If both conditions hold, RATUS succeeds. If either fails, RATUS
fails. The two distinct ways to fail (wrong shape vs. correct shape
but value not exhausted) are NOT distinguished for penalty purposes
— both receive the same failure penalty.

Failure ends the game exactly like success does — the maker forced
their hand empty, so the game cannot continue either way. When
RATUS fails, there is no winner: `winner` is `None`.

## Penalty

- Success: the maker receives -50. Every other player receives +50
  each.
- Failure: the maker receives +15. No other player is penalized.

## Relationship to FinishType and SpecialResult

`finish_type = FinishType.RATUS` whenever the winning Move's
`move_type` is `MoveType.RATUS`, regardless of success or failure.
`special_result` then distinguishes the outcome:

- `SpecialResult.RATUS` if the attempt succeeded (winner is the
  maker).
- `SpecialResult.FAILED_RATUS` if the attempt failed (winner is
  `None`).

---

# RIBU Philosophy

RIBU follows the same "optional strategic Move" philosophy as
RATUS: it is triggered purely by the action of playing three
remaining dominoes together as a single Move, never by hand state
alone, and is never mandatory.

## Trigger and Shape Requirement

Unlike RATUS, RIBU has a mandatory hand-shape requirement enforced
by MoveGenerator at generation time: the three dominoes must consist
of exactly two double dominoes of two different values, plus exactly
one connecting domino whose two sides match those two values. If a
player's last three dominoes do not have this shape, RIBU is never
offered as an option by MoveGenerator — the three dominoes may still
be played individually as three separate NORMAL moves, but not as a
single RIBU Move.

Within a hand that does have the correct shape, more than one
physical arrangement of the three dominoes may be legal (for
example, the three dominoes may close the table on either of the
two double values, depending on how they are distributed between
the two ends). MoveGenerator offers every such legal arrangement;
which one is played is the player's choice.

A Move is atomic, same as RATUS and NORMAL: if any one of the three
Placements fails, the entire RIBU Move is rejected.

## Success and Failure

After a RIBU Move is played and the maker's hand is empty:

1. **Shape**: both ends of the table must be equal after the Move.
   If not, RIBU fails immediately (a failure of shape), regardless
   of hand-shape correctness at generation time — the hand-shape
   check at generation time does not guarantee a symmetric closing
   result for every possible table state.
2. **Exhaustion**: if the shape is correct, BOTH of the two double
   values used in the Move (not only whichever value the table
   happened to close on) must be exhausted from every other player's
   hand.

Both failure modes receive the same failure penalty, exactly as
with RATUS. When RIBU fails, there is no winner: `winner` is `None`.

## Penalty

- Success: the maker receives -50. Every other player receives +20
  each.
- Failure: the maker receives +25. No other player is penalized.

## Relationship to FinishType and SpecialResult

Same pattern as RATUS: `finish_type = FinishType.RIBU` whenever the
winning Move's `move_type` is `MoveType.RIBU`, regardless of outcome.
`special_result` is `SpecialResult.RIBU` on success or
`SpecialResult.FAILED_RIBU` on failure.

---

# Local Rule Priority

Whenever the local Kalimantan Gaple rules differ from international domino rules, the local rulebook always takes priority.

The engine must never replace documented local rules with assumptions based on international domino standards.

---

# Documentation Philosophy

Documentation is considered correct until an intentional revision is approved.

MASTER_CORE.md is the highest authority within the project.

AI assistants must never invent undocumented rules.

Whenever documentation and implementation disagree, documentation takes precedence.

Whenever a rule has not yet been specified in this document, AI assistants must report the gap and request clarification rather than inventing behavior to fill it.

---

# Testing Philosophy

The project follows Test-Driven Development (TDD).

Every new rule should be introduced through tests before implementation.

Foundation tests verify stable engine components.

Rule tests verify behavior defined by the local Gaple rulebook.

Documentation should be updated before implementing rule changes.

---

# Permanent Principles

- The engine has no user interface.
- Each class has exactly one responsibility.
- Game executes gameplay only.
- RuleSystem evaluates finished games only.
- Match manages multiple games.
- Artificial intelligence belongs outside the engine.
- Documentation is the single source of truth.
- Local Kalimantan rules always take precedence over international domino rules.
- Engine behavior must remain deterministic.
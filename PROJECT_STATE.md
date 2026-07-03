# PROJECT_STATE.md

Version: 4.6

Status: Active

Last Updated: 2026-07-03

---

# Project State

Current Development Phase

Milestone 2

Rule Engine

---

# Architecture Freeze

The following design decisions are considered stable and should not
be changed unless the official rulebook changes or a verified bug is
found. This list is a practical summary for quick reference; if it
ever appears to conflict with MASTER_CORE.md, MASTER_CORE.md is the
authority and this list is wrong and must be corrected.

- Domino comparison for DOM Step 4 is pip-sum based, not tile-order
  based.
- RuleSystem is responsible only for evaluating completed games.
- Game records facts; RuleSystem evaluates rules.
- Table never determines finish type.
- MoveGenerator never applies scoring logic.
- PASAR is detected from table state before the final move, never
  from pass_count.

---

# Current Assumptions

- Four players only.
- No partnership mode.
- Indonesian Gaple (Kalimantan local rule), not international
  domino rules.
- 28-tile double-six set.

---

# Engine Invariants

Every change must preserve:

- RuleSystem tests stay green.
- MoveGenerator never decides scoring.
- RuleSystem never mutates game state.
- Game stores facts only.
- Table stores facts only.
- DOM tie-break steps only evaluate players still tied from the
  previous step; a player eliminated at an earlier step is never
  reconsidered later.
- Step 3b and Step 4 raise RuntimeError instead of silently
  guessing when a tie is unexpectedly unresolved.

---

# Rule Engine Baseline v1.0

Established: 2026-07-03

This marker is an internal reference point, not a public release. It
exists so that if a future change (starting with GUPLAH) causes
unexpected regressions, there is a known-good point to compare
against.

Coverage at this baseline:

- ✓ DOM rulebook (finish detection, winner, full tie-break Step 1
  through Step 4 including balak sub-steps 3a/3b, scoring)
- ✓ PASAR rulebook (finish detection, scoring, reusing DOM's
  tie-break sequence)
- ✓ 22 RuleSystem tests passing
- ✓ MASTER_CORE.md, AI_CONTEXT.md, and PROJECT_STATE.md in sync
  with the implementation

Known gaps at this baseline (intentionally not yet closed):

- `RuleSystem.evaluate(game)` can still be called on a game that
  has not finished, silently returning `FinishType.NORMAL` instead
  of rejecting the call. The rulebook for DOM and PASAR is complete;
  this is a RuleSystem *contract* gap, not a rulebook gap.

---



## Milestone 1

Core Engine

Status:

✅ Completed

Implemented modules:

- Domino
- Deck
- Player
- Table
- Move
- MoveGenerator
- TurnResult
- Game
- GameEndResult

Core gameplay is stable.

All foundation tests are passing.

---

## Milestone 2

Rule Engine

Status:

≈ 80% Complete

Completed:

- ✓ DOM finish detection
- ✓ DOM winner detection
- ✓ DOM penalty tie-break (Step 1 through Step 4, including the
  balak sub-steps 3a and 3b)
- ✓ DOM scoring (-3 winner / +3 penalty recipient)
- ✓ PASAR finish detection (structural detection, based on table
  state before the final move)
- ✓ PASAR scoring (-4 winner / +4 penalty recipient, reusing the
  exact same tie-break sequence as DOM)

In Progress / Not Started:

- GUPLAH detection
- GUPLAH penalty
- RATUS
- RIBU
- Special Result evaluation

---

## Milestone 3

Match Engine

Status:

⏳ Not Started

Planned responsibilities:

- Multiple Game management
- Opening player rotation
- Match score accumulation
- Match winner detection

---

## Milestone 4

Analysis Engine

Status:

⏳ Not Started

Planned responsibilities:

- Match replay
- Statistics
- Strategy analysis
- AI training support

---

# Open Design Questions

These are not bugs and not pending implementation work. They are
local rules that have not yet been decided by the project owner.
Implementations must not guess at answers to these questions.

- GUPLAH penalty: the winner rule is already defined (smallest
  remaining pip total), but the penalty rulebook is not yet
  specified, and must not be assumed to reuse DOM's tie-break
  sequence.
- Special Result interaction: how SpecialResult should interact
  with finish_type and penalty_changes once GUPLAH, RATUS, and RIBU
  exist alongside DOM and PASAR.

---

# Regression History

This section records confirmed bugs that were found and fixed,
so the reasoning does not have to be rediscovered later.

## MASTER_CORE.md v4.3 / rule_system.py (this session)

Three separate issues were found and fixed together, because
resolving the DOM balak tie-break required re-examining the whole
DOM penalty flow:

1. **Step 4 domino comparison was tile-order based, not pip-sum
   based.** MASTER_CORE.md v4.1 and v4.2 both documented Step 4 as
   "compare the higher value, then the lower value" (tile-order).
   This was proven incorrect using a concrete counter-example
   (6-0 vs 5-4): tile-order would select the 6-0 holder, but the
   confirmed local rule selects the 5-4 holder, because pip sum
   (9 vs 6) is compared first. Both the documentation and
   `domino_rank()` were corrected to be pip-sum based.

2. **Multiple-balak-holder tie-break was undefined, then
   underspecified.** MASTER_CORE.md v4.0 did not address balak at
   all. v4.1 introduced a single balak step but only covered
   "exactly one holder" and "no holders." v4.2 attempted to handle
   multiple holders by narrowing candidates and falling through to
   Step 4, but this was found to contradict the actual local rule:
   balak-vs-balak comparison never considers non-double dominoes at
   all. The confirmed rule, now Step 3a (balak count) and Step 3b
   (highest balak value), never falls through to Step 4.

3. **PASAR was detected using `pass_count >= 4`,** which directly
   violated an explicit rule already written in AI_CONTEXT.md
   ("do not model PASAR as merely four consecutive PASS actions").
   Fixing this required two small factual additions, consistent
   with the Game/Table-records-facts-only philosophy:
   - `Game.last_move`: the last move actually played.
   - `Table.previous_left_end` / `previous_right_end`: table ends
     immediately before the last move was applied.

Additionally, `find_dom_loser`'s Step 3b and Step 4 were changed
from silently returning `candidates[0]` on an unresolved tie to
raising `RuntimeError`, so future bugs surface immediately instead
of producing a silently wrong penalty recipient.

## test_rule_system.py (this session)

`fill_all_players` previously gave every player an identical hand
(`Domino(0, 0)`). Once Step 3b became strict, this caused a
genuine, unresolvable 3-way tie (all non-winner players had
identical pip total, card count, and balak value), which is not a
realistic game state. The fixture was corrected to give each player
a distinct, non-double pip total.

## PASAR scoring (follow-up session)

PASAR scoring was confirmed by the project owner to reuse the exact
same tie-break sequence as DOM (Step 1 through Step 4), differing
only in penalty magnitude: DOM applies -3/+3, PASAR applies -4/+4.
`calculate_pasar_score` now calls the same `find_dom_loser` used by
DOM rather than duplicating the tie-break logic, so any future fix
to the tie-break sequence automatically applies to both finish
strategies.

---

# Immediate Next Tasks

1. Design and implement GUPLAH detection (blocked game).
2. Design and implement the GUPLAH penalty rulebook.
3. Implement RATUS.
4. Implement RIBU.
5. Complete Special Result evaluation.
6. Guard RuleSystem.evaluate against being called on an unfinished
   game (currently falls through to FinishType.NORMAL silently).
7. Begin Match Engine.

---

# Testing Status

Development follows Test-Driven Development (TDD).

Rules:

- Write tests before implementation whenever possible.
- Keep all existing tests passing after every change.
- Never introduce new features by breaking existing tests.

Current foundation tests:

✅ Passing

Current RuleSystem tests:

✅ Passing (20/20)

---

# Future Modules

After the engine reaches a stable release, the following modules are
planned:

- ⏳ Strategy Analyzer
- ⏳ AI Player
- ⏳ REST API
- ⏳ Mobile App
- ⏳ Web App

---

# Current Goal

Current priority is correctness rather than speed.

The objective is to produce a clean, modular, and maintainable
Gaple Engine that accurately models the local Kalimantan rulebook
before expanding into higher-level features.

Engine stability always takes priority over rapid feature
development.
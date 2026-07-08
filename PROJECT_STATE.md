# PROJECT_STATE.md

Version: 4.9

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
- Move stores a list of Placements, not a single domino/side pair.
  There is no `Move.dominoes` / `Move.side` compatibility alias.
- MoveGenerator does not require any particular shape for RATUS's
  two dominoes (shape-agnostic); it DOES require a specific shape
  for RIBU's three dominoes (two doubles + one matching connector)
  before offering it as an option.
- RATUS/RIBU success or failure is decided by RuleSystem after the
  Move is played, never by MoveGenerator at generation time.

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
- A Move is atomic: Table.play() either applies every Placement
  successfully, or rolls back to the exact pre-Move state and
  raises. No half-applied Move is ever left on the table.
- RATUS and RIBU never distinguish "wrong shape" failure from
  "value not exhausted" failure in penalty terms — both receive
  the same failure penalty.

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

100% Complete

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
- ✓ GUPLAH detection (blocked game, using game.game_over as the
  underlying fact)
- ✓ GUPLAH maker identity (game.last_move_player, a new fact
  recorded by Game)
- ✓ GUPLAH winner (smallest pip, GUPLAH-maker override, then
  Step 2/3/3a/3b/4 with every direction reversed from DOM)
- ✓ GUPLAH scoring (-5 winner; +5 to everyone else if the maker
  is the winner, otherwise +5 to only the maker and 0 to everyone
  else)
- ✓ FinishType.GUPLAH added to game_end_result.py, alongside
  NORMAL/DOM/PASAR
- ✓ SpecialResult.GUPLAH / SpecialResult.FAILED_GUPLAH wired up:
  set together with FinishType.GUPLAH, marking whether the GUPLAH
  maker won or lost
- ✓ Move migrated from a single domino/side model to
  `placements: list[Placement]`, enabling multi-placement moves
  (see Regression History for the full migration summary)
- ✓ Table.play() made atomic: a Move either fully succeeds or is
  fully rolled back, no partial application
- ✓ RATUS detection, MoveGenerator generation (shape-agnostic,
  action-triggered), success/failure evaluation (shape then
  exhaustion), and scoring (-50/+50 success, +15/0 failure)
- ✓ RIBU detection, MoveGenerator generation (shape-mandatory: 2
  doubles + 1 connector, multiple valid distributions offered),
  success/failure evaluation (shape then dual-value exhaustion),
  and scoring (-50/+20 success, +25/0 failure)
- ✓ FinishType.RATUS / FinishType.RIBU added to game_end_result.py
- ✓ SpecialResult.RATUS / FAILED_RATUS / RIBU / FAILED_RIBU wired
  up, following the same pattern as GUPLAH

In Progress / Not Started:

- Special Result evaluation for any finish type beyond GUPLAH,
  RATUS, and RIBU (none currently known to be needed)

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

None currently open. (RATUS and RIBU's SpecialResult interaction,
previously listed here, is resolved — see the RATUS/RIBU Philosophy
sections in MASTER_CORE.md.)

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

## GUPLAH design and implementation (follow-up session)

GUPLAH required the most extensive back-and-forth of any finish
strategy so far, because the local rule has two layers that are
easy to conflate: the pip-based winner rule (already partially
known from earlier sessions) and the identity of the "GUPLAH
maker" (the player who last successfully played before the block),
which turned out to override the pip-based tie-break entirely when
the maker is one of the tied candidates.

Key decisions confirmed through concrete examples:

- GUPLAH winner Step 2 through Step 4 mirror DOM's tie-break
  sequence structurally, but every comparison direction is
  reversed (fewest dominoes, absence of balak, fewest/lowest-valued
  balak, and lowest-ranked highest domino all favor the winner
  here, since GUPLAH looks for the lightest burden instead of the
  heaviest one).
- The GUPLAH-maker override sits between Step 1 and Step 2: if the
  maker is among the players tied for smallest pip, the maker wins
  immediately regardless of what Step 2 onward would have produced.
  If the maker already lost at Step 1, the override never applies
  and Step 2 onward runs exactly as if the maker did not exist.
- GUPLAH penalty has two distinct modes depending on whether the
  maker is the winner. An earlier draft of this rule (recorded in
  AI_CONTEXT.md v4.2, since corrected) assumed "everyone who is not
  the winner gets penalized," which is only true in the mode where
  the maker and the winner are the same player.

Implementation notes:

- `find_guplah_winner` is a separate function from `find_dom_loser`
  (not a reuse), because the candidate set and override logic are
  fundamentally different: GUPLAH considers all players (nobody
  emptied their hand), while DOM excludes the winner from
  consideration.
- The underlying comparison primitives (`domino_rank`,
  `highest_domino`, `_balak_dominoes`, `_highest_balak_value`) are
  shared with DOM rather than duplicated.
- `Game` gained one more recorded fact: `last_move_player`, the
  identity of whoever played `last_move`. This follows the same
  minimal, facts-only pattern established for PASAR's
  `previous_left_end` / `previous_right_end`.

## GUPLAH FinishType missing from game_end_result.py (follow-up session)

The initial GUPLAH implementation referenced `FinishType.GUPLAH`
without first reading `game_end_result.py`, which had never been
shared in the session up to that point. `FinishType` only defined
NORMAL, DOM, and PASAR; GUPLAH (along with RATUS, RIBU, and their
FAILED_* variants) already existed, but inside `SpecialResult`
instead, left over from an earlier architecture decision recorded
in PROJECT_STATE.md ("the engine should instead model five
independent winning strategies") that was never fully carried
through to `game_end_result.py`.

This was caught immediately by a full pytest run (13 failures, all
`AttributeError: type object 'FinishType' has no attribute
'GUPLAH'`) rather than silently producing wrong behavior, because
the attribute access fails loudly. The fix was to add
`FinishType.GUPLAH` alongside NORMAL/DOM/PASAR, and to clarify that
`SpecialResult.GUPLAH` / `SpecialResult.FAILED_GUPLAH` serve a
different purpose: they mark whether the GUPLAH maker succeeded,
and are set together with `FinishType.GUPLAH`, not instead of it.

Lesson recorded here deliberately: do not reference an enum member
or field on a class that has not been shown in the current session,
even when its name seems obvious from context. Ask to see the file
first.

## RuleSystem.detect_special_result signature change (follow-up session)

`detect_special_result(game)` became `detect_special_result(game,
finish_type, winner)`, because deciding between
`SpecialResult.GUPLAH` and `SpecialResult.FAILED_GUPLAH` requires
knowing both the finish type and who the winner is. No test called
`detect_special_result` directly before this change, so nothing
outside `evaluate()` needed updating.

## Move/Placement migration and RATUS/RIBU implementation (follow-up session)

This was the largest structural change since the project began. It
was carried out in four explicit phases, tracked in
`MOVE_REFACTOR_PLAN.md` (now archived/removed — its purpose was
temporary, per its own stated policy), specifically to keep pure
refactoring (no behavior change) separate from RATUS/RIBU feature
work (new behavior), so that a bug during either phase would be
unambiguous about its cause.

**Why the migration was needed**: `Move` originally stored a single
`dominoes: list[Domino]` and one `side: Side` for the entire move.
RATUS (two dominoes on potentially different sides) and RIBU (three
dominoes) cannot be represented this way. `Move` was migrated to
`placements: list[Placement]`, where `Placement` pairs one domino
with one side. This was a full migration — no `Move.dominoes` /
`Move.side` compatibility alias was kept, matching the project's
established preference for a single source of truth over
convenience aliases (the same reasoning applied when GUPLAH's
`FinishType` was added directly rather than left split across two
enums).

**Phase 1** added `Placement` alongside the untouched old `Move`
model. **Phase 2** migrated `Move`, `Table`, `Game`, `MoveGenerator`,
and `RuleSystem` to use `placements`, including extracting `Side`
into its own `side.py` to avoid a circular import between `move.py`
and `placement.py`. **Phase 3** was a review pass confirming DOM,
PASAR, and GUPLAH behavior was unchanged. **Phase 4** implemented
RATUS and RIBU on top of the now-stable `Placement` model.

**Two bugs were found and fixed during Phase 2/3, both self-inflicted
test-authoring mistakes rather than migration bugs**: a test
constructing a 2-placement Move without setting `move_type=RATUS`
(defaulted to NORMAL, correctly rejected by `Move`'s own validation),
and a `str_replace` edit that accidentally deleted a test function's
`def` line, silently merging its body into the previous test — caught
immediately by a syntax check before being handed back.

**`Table.play()` was made atomic** as part of this work: if any
Placement within a multi-placement Move fails, the entire Move is
rolled back (chain, left_end, right_end restored to their pre-Move
values) rather than leaving the table half-mutated. This was
identified as necessary specifically because RATUS/RIBU introduced
multi-placement Moves where a mid-move failure became newly possible
in principle (even though `MoveGenerator` is expected to only offer
already-legal combinations).

**RATUS and RIBU rule design** took the same "rule via concrete
examples first" approach used for DOM/PASAR/GUPLAH, and surfaced two
non-obvious findings before any code was written:

- RATUS is action-triggered (playing 2 remaining dominoes together),
  never inferred from hand contents, and is optional — a player
  meeting RATUS's conditions may still choose NORMAL. `MoveGenerator`
  does not check the shape of the two dominoes at all; it offers
  every legal combination, including ones that will fail, because a
  wrong choice is a genuine playable mistake in the local rule, not
  something the engine should prevent.
- RIBU, by contrast, DOES require a specific hand shape at generation
  time (exactly two doubles of different values plus one connector
  joining them) — `MoveGenerator` will not offer RIBU at all for a
  hand that doesn't match this shape, even if the three dominoes are
  otherwise physically connectable. Within a correctly-shaped hand,
  more than one legal placement arrangement can exist (the three
  dominoes can close the table on either of the two double values),
  and `MoveGenerator` offers all of them.
- Both RATUS and RIBU can fail in two distinct ways — wrong shape
  (table ends not equal after the move) or correct shape but the
  relevant domino value(s) not yet exhausted from other players'
  hands — and both failure modes receive an identical penalty; they
  are not distinguished in scoring.
- When RATUS or RIBU fails, there is no winner (`winner = None`),
  unlike GUPLAH (which always has a winner regardless of whether the
  maker succeeded).

**Implementation notes**: `find_guplah_winner` and `find_dom_loser`
were deliberately NOT reused for RATUS/RIBU winner determination —
RATUS/RIBU winner logic is trivial (the maker, if successful) and
structurally unrelated to DOM/GUPLAH's tie-break search. The
combination-search algorithm for RATUS/RIBU placement generation
(`MoveGenerator._generate_multi_placement_moves`) is shared between
both, driven by a new pure, side-effect-free
`Table.simulate_placement` static method, so the connection-legality
logic itself is never duplicated between `Table` and
`MoveGenerator`.

All 101 tests passed on the first real pytest run after this entire
migration and feature implementation — the most complex single unit
of work in the project's history to date.

---

# Immediate Next Tasks

1. Guard RuleSystem.evaluate against being called on an unfinished
   game (currently falls through to FinishType.NORMAL silently).
2. Begin Match Engine.

---

# Testing Status

Development follows Test-Driven Development (TDD).

Rules:

- Write tests before implementation whenever possible.
- Keep all existing tests passing after every change.
- Never introduce new features by breaking existing tests.

Current foundation tests:

✅ Passing (deck, player, move, table, move_generator, game,
game_end_result)

Current RuleSystem tests:

✅ Passing. Full test suite across the entire project: 101 tests,
all passing on the first real pytest run after the Move/Placement
migration and RATUS/RIBU implementation (see Regression History for
the full account of what was built and verified).

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
# MOVE_REFACTOR_PLAN.md

Status: Active (temporary — to be archived into PROJECT_STATE.md
Regression History once migration is complete)

---

# Purpose

This document tracks the migration of `Move` from a single-placement
model to a multi-placement model, so that RATUS (and later RIBU) can
be represented as one Move containing several placements instead of
one Move with one domino and one side.

This document exists only for the duration of the migration. Once
Phase 4 is complete, its contents should be summarized as one entry
in `PROJECT_STATE.md`'s Regression History, and this file should be
archived or deleted — it is not a fourth permanent core document
alongside MASTER_CORE.md, AI_CONTEXT.md, and PROJECT_STATE.md.

---

# Why this migration is needed

`Move` currently stores exactly one domino and one `Side` for the
entire move:

```
Move
 ├── dominoes: list[Domino]
 ├── side: Side          <- ONE side for the whole move
 ├── move_type
```

RATUS requires two dominoes placed on two DIFFERENT sides within one
single move (one double domino closing the end that already matches,
one connecting domino closing the other end). A single `side` field
cannot represent this.

---

# Current Model → Target Model

```
Current Model

Move
 ├── dominoes: list[Domino]
 ├── side: Side
 ├── move_type: MoveType

↓

Target Model

Move
 ├── placements: list[Placement]
 ├── move_type: MoveType

Placement
 ├── domino: Domino
 ├── side: Side
```

`Placement` is a new class. It is NOT the same thing as
`PlacedDomino` (in `placed_domino.py`), even though the names are
similar:

- `Placement` = an instruction, BEFORE being applied to the table
  (which domino, which side it is aimed at). Belongs to `Move`.
- `PlacedDomino` = a recorded fact, AFTER being applied to the table
  (which domino, what its outward/inward values ended up being once
  woven into the chain). Belongs to `Table.chain`.

They answer different questions and both remain, unchanged in
purpose.

---

# Two separate kinds of work — do not mix them

1. **Refactoring** (Phases 1–3): change the data structure. No new
   engine capability. DOM, PASAR, GUPLAH must behave identically
   before and after.
2. **Feature work** (Phase 4): implement RATUS. This is the only
   phase allowed to add new engine behavior.

If a bug appears during Phases 1–3, it is a refactor bug — the fix
is to make behavior match what it was before, nothing more. If a bug
appears during Phase 4, it is a RATUS logic bug. Keeping these
separate in commits and in reasoning is the entire point of this
plan.

---

# Non-goals

This migration does NOT aim to:

- Change any rule in `RuleSystem` (DOM, PASAR, or GUPLAH logic and
  outcomes must stay identical).
- Change DOM, PASAR, or GUPLAH penalty values or tie-break order.
- Add AI strategy or decision-making of any kind.
- Change `MoveGenerator`'s NORMAL-move algorithm beyond adapting its
  output to `Placement` (Phases 1–3 must not alter which moves are
  considered legal, only how a legal move is represented).
- Optimize performance, restyle unrelated code, or rename anything
  not directly required by the `Placement` migration.

One clarification, since it could otherwise look contradictory:
`rule_system.py` IS touched in Phase 2 (`_is_pasar` reads
`move.placements[0].domino` instead of `move.dominoes[0]`). This is
in scope, because it is purely adapting to the new `Move` shape — no
PASAR rule, tie-break, or penalty value changes as a result. Touching
the file is fine; changing what it decides is not.

If an idea comes up during this migration that is not covered by the
checklists below, the test is simple: does it appear in this plan?
If not, it is out of scope — write it down in `PROJECT_STATE.md`
instead of doing it now, no matter how small or tempting it seems in
the moment.

---

# Phase 1 — Add the new abstraction, alongside the old one

Goal: introduce `Placement` as a building block. Nothing else changes
yet. `Move` still uses `dominoes` / `side` exactly as today.

Checklist:

- [ ] Create `placement.py` with the `Placement` dataclass
      (`domino`, `side`).
- [ ] No other file is touched.

Checkpoint:

- ✅ All 35 existing RuleSystem tests still pass, untouched.
- ✅ `Placement` has no test yet referencing it from `Move`, `Table`,
      `Game`, or `MoveGenerator` — it is inert at this point.

---

# Phase 2 — Migrate Move itself

Goal: `Move` switches from `dominoes` / `side` to
`placements: list[Placement]`. Every file that constructs or reads a
`Move` is updated to match. `MoveGenerator` still only ever produces
one-placement (NORMAL) moves — no RATUS yet.

Checklist:

- [ ] Resolve the `Side` circular import first: `placement.py`
      (from Phase 1) imports `Side` from `move.py`, but `move.py` is
      about to need `Placement` from `placement.py` — a direct
      circular import. Extract `Side` (and, if convenient,
      `MoveType`) out of `move.py` into its own file (e.g.
      `side.py`), and update both `move.py` and `placement.py` to
      import it from there instead.
- [ ] `move.py`: replace `dominoes` / `side` with
      `placements: list[Placement]`. `__post_init__` validates
      `len(self.placements)` against `move_type` (same rule as
      before: 1 for NORMAL, 2 for RATUS, 3 for RIBU). Decide and
      document the new `__str__` format (old format
      `"NORMAL: [6-6] -> LEFT"` assumed a single domino/side and no
      longer fits a multi-placement move cleanly).
- [ ] `table.py`: `Table.play(move)` loops over `move.placements`,
      applying each `(domino, side)` in order — one at a time, not
      validated all up front, since a later placement's legality can
      depend on the table state left behind by an earlier placement
      in the same move. `Table.can_play(domino, side)` itself is
      NOT changed — its signature already matches `Placement`
      exactly.
- [ ] `game.py`: `player.play(move.dominoes[0])` becomes a loop:
      `for placement in move.placements: player.play(placement.domino)`.
- [ ] `rule_system.py`: `_is_pasar` reads
      `move.placements[0].domino` instead of `move.dominoes[0]`. Add
      an explicit guard: if `len(move.placements) != 1`, PASAR does
      not apply (PASAR and DOM are only ever produced by
      single-placement moves at this stage of the engine).
- [ ] `move_generator.py`: wrap each generated domino/side pair into
      a single-item `placements` list. Behavior is otherwise
      unchanged — still one Move per legal domino/side combination.
- [ ] Update tests: `test_move.py`, `test_table.py`, `test_game.py`,
      `test_move_generator.py` all rewritten to construct
      `Move(placements=[Placement(...)], ...)` instead of
      `Move(dominoes=[...], side=...)`.
- [ ] Update `test_rule_system.py`: the hand-built fake `Move` object
      used for PASAR tests (`type("FakeMove", (), {"dominoes": [...]})()`)
      is replaced with a real `Move` using `placements`.

Checkpoint:

- ✅ All tests across `test_move.py`, `test_table.py`, `test_game.py`,
      `test_move_generator.py`, and `test_rule_system.py` pass again.
- ✅ Engine still plays NORMAL, DOM, PASAR, and GUPLAH identically to
      before — verified by re-running `simulate.py` and confirming
      the same kind of end-to-end behavior seen previously.
- ✅ No `Move.dominoes` or `Move.side` remains anywhere in the
      codebase (full migration, no compatibility alias, as agreed).

---

# Phase 3 — Confirm internal consistency, no behavior change

Goal: this is a review/hardening phase, not new code. By the end of
Phase 2, `Game`, `Table`, `RuleSystem`, and `MoveGenerator` already
use `Placement` throughout. Phase 3 is where we deliberately look for
anything Phase 2 may have missed, before RATUS adds real complexity
on top.

Checklist:

- [ ] Re-read `game.py`, `table.py`, `rule_system.py`,
      `move_generator.py` end to end, specifically hunting for any
      remaining assumption of "exactly one domino per move" that
      Phase 2 may not have caught.
- [ ] Confirm `GameEndResult`, `TurnResult`, and any other model that
      references a `Move` does not assume single-placement structure.
- [ ] Full regression run: all tests green, `simulate.py` run at
      least once more.

Checkpoint:

- ✅ DOM, PASAR, GUPLAH behavior is byte-for-byte identical to Phase
      0 (pre-migration) behavior. If anything differs, that is a
      refactor bug and must be fixed before Phase 4 starts — RATUS
      work does not begin on top of an unverified refactor.

---

# Phase 4 — Implement RATUS (feature work begins here)

Goal: only now does the engine gain a new capability. Everything
before this line was pure refactoring.

Checklist:

- [ ] `move_generator.py`: add logic to detect legal RATUS
      combinations — a double domino placed on the end it already
      matches, paired with a connecting domino that closes the other
      end to the same value — and emit them as two-placement
      `MoveType.RATUS` moves, alongside (not instead of) the normal
      one-placement moves. MoveGenerator does not choose a strategy;
      it only reports every legal option, RATUS included, same as it
      always has for NORMAL moves.
- [ ] Resolve the still-open RATUS rule questions from the earlier
      discussion (finish detection, `FinishType.GUPLAH`-style
      addition of `FinishType.RATUS`, `SpecialResult.RATUS` /
      `FAILED_RATUS` wiring, the temporary -50/+50 and +15 penalty
      values pending Match Engine, and whether the maker must have
      exactly zero cards left after the RATUS placements to succeed).
- [ ] New tests written before implementation, following the
      project's TDD rule.

Checkpoint:

- ✅ New RATUS-specific tests pass.
- ✅ All prior tests (DOM/PASAR/GUPLAH, Phase 1–3 refactor tests)
      still pass unchanged.

---

# What happens after Phase 4

Once Phase 4 is complete and all tests are green:

1. Summarize this entire migration (Phases 1–4) as one entry in
   `PROJECT_STATE.md`'s Regression History.
2. Update `MASTER_CORE.md` and `AI_CONTEXT.md` with the finalized
   RATUS rulebook.
3. Archive or delete this file — it has served its purpose.
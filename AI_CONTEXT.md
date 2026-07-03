# AI_CONTEXT.md

Version: 4.4

---

# Gaple Engine AI Context

Always read MASTER_CORE.md before suggesting code.

MASTER_CORE.md is the highest authority of this project.

If any implementation, previous discussion, or existing code conflicts with MASTER_CORE.md, follow MASTER_CORE.md.

---

# Architecture

Game

↓

RuleSystem

↓

Match

---

# Layer Responsibilities

## Game

Responsible only for gameplay.

Game:

- validates legal moves
- manages turn order
- manages table state
- records passes
- detects that gameplay has finished

Game never determines:

- DOM
- PASAR
- GUPLAH
- RATUS
- RIBU

Game records facts only.

---

## RuleSystem

RuleSystem evaluates a finished Game.

RuleSystem determines:

- winner
- finish strategy
- special result
- penalty changes

RuleSystem never changes gameplay.

---

## Match

Match manages multiple Game objects.

Match is responsible for match progression only.

---

# Finish Strategy Philosophy

Gaple defines five finish strategies.

These strategies are considered equal.

The engine never prioritizes one finish strategy over another.

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

# DOM Design Decision

DOM occurs when a player legally plays their final domino.

Winner:

The player who empties their hand.

Penalty recipient:

Penalty determination follows a candidate elimination process.

Tie-break order:

1. Largest remaining pip total.
2. Greatest number of remaining dominoes.
3. Double domino (balak), evaluated through Step 3.0, Step 3a, and Step 3b as defined in MASTER_CORE.md.
4. Highest remaining domino, using a pip-sum-based comparison.

Each step evaluates only the players who remain tied from the previous step.

Players eliminated during an earlier step are never reconsidered.

Step 3 is evaluated only among players still tied after Step 2.

A player outside the tied group is never considered, even if that player holds one or more double dominoes.

If none of the tied players holds a double domino, skip Step 3 entirely and move to Step 4 using all remaining tied players.

If exactly one tied player holds one or more double dominoes, that player receives the penalty immediately. This does not proceed to Step 3a, Step 3b, or Step 4.

If two or more tied players each hold one or more double dominoes, eliminate every tied player who holds no double domino, then resolve the tie among the remaining balak-holding players as follows:

- Step 3a: compare how many double dominoes each of them holds. The player holding the greatest number of double dominoes receives the penalty.
- Step 3b: if the number of double dominoes held is also tied, compare the pip value of each player's own highest double domino. This comparison uses only the value of the double dominoes themselves — non-double dominoes held by these players are irrelevant at this step. The player holding the highest-valued double domino receives the penalty.

Step 4 is never reached when Step 3a or Step 3b resolves the tie. Step 4 is reached only when no tied player holds a double domino at all.

Step 4 compares each remaining player's highest-ranked domino.

To identify a player's own highest-ranked domino, and then to compare that domino across players, use the same order:

1. Compare the pip sum (the two sides added together).
2. If equal, compare the higher single value.
3. If still equal, compare the lower single value.

Do not rank dominoes by comparing the higher single value first. The pip sum is always compared first.

Because every domino in a standard double-six set is unique, and because each domino being compared belongs to a different player, Step 4 always produces a single deterministic penalty recipient.

---

# PASAR Design Decision

PASAR is a special form of DOM.

The final domino must be legally playable on both open ends of the table simultaneously.

PASS count is irrelevant.

Do not model PASAR as merely four consecutive PASS actions.

Winner determination follows DOM.

Penalty determination follows the exact same tie-break sequence as
DOM (Step 1, Step 2, Step 3.0/3a/3b, Step 4 as defined above). Reuse
the DOM tie-break logic — do not write a separate implementation.

The only difference from DOM is the penalty magnitude: DOM applies
-3/+3, PASAR applies -4/+4. This is because PASAR is a stronger
finish than DOM under the local Kalimantan rulebook (the final
domino must be playable on both ends at once), so the same tie-break
outcome is rewarded with a larger swing.

---

# GUPLAH Design Decision

GUPLAH occurs when gameplay becomes blocked.

The player causing the block is not automatically the winner.

Winner:

The player with the smallest remaining pip total. This winner rule is already defined in MASTER_CORE.md and is not pending specification.

Penalty:

Penalty determination follows the GUPLAH rulebook.

The GUPLAH penalty rulebook has not yet been formally specified. Do not assume single-recipient or multi-recipient penalty behavior for GUPLAH.

Do not reuse the DOM tie-break sequence (pip total, domino count, balak, highest domino) for GUPLAH. GUPLAH ranks players by the smallest pip total rather than the largest, so its tie-break logic must be designed independently and cannot be assumed to mirror DOM.

---

# Development Philosophy

Always preserve the project architecture.

Never bypass RuleSystem.

Never move gameplay rules into Game.

Implement new rules through Test-Driven Development.

Documentation must be updated before changing rule behavior.

Never redesign the architecture without first updating MASTER_CORE.md.

When documentation and implementation disagree, documentation is always correct.

Never invent local rules that are not documented.

When uncertain, request clarification instead of making assumptions.
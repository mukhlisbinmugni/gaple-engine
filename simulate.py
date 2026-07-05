from game import Game
from rule_system import RuleSystem


game = Game()
game.start()

print("=" * 60)
print("GAPLE ENGINE SIMULATION")
print("=" * 60)

turn = 1

while not game.is_over():

    result = game.play_turn()

    print(f"\nTurn {turn}")

    if result.status.name == "PASS":
        print(f"{result.player.name} PASS")
    else:
        placements_str = ", ".join(
            f"{p.domino.left}-{p.domino.right}"
            for p in result.move.placements
        )

        print(
            f"{result.player.name} memainkan "
            f"{placements_str}"
        )

    turn += 1

print("\n" + "=" * 60)
print("SISA TANGAN")
print("=" * 60)

for player in game.players:
    hand_str = ", ".join(
        f"{d.left}-{d.right}" for d in player.hand
    ) if player.hand else "(kosong)"

    print(f"{player.name}: {hand_str}")

print("\n" + "=" * 60)
print("GAME OVER")
print("=" * 60)

evaluation = RuleSystem.evaluate(game)

penalty_str = ", ".join(
    f"{player.name}: {change}"
    for player, change in evaluation.penalty_changes.items()
)

print(f"Finish Type : {evaluation.finish_type}")
print(f"Winner      : {evaluation.winner.name}")
print(f"Penalty     : {penalty_str}")

print("=" * 60)
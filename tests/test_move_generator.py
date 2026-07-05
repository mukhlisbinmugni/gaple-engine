from domino import Domino
from move import Move
from placement import Placement
from side import Side
from move_generator import MoveGenerator
from table import Table


def test_empty_table_generates_one_move_per_domino():
    table = Table()

    hand = [
        Domino(6, 6),
        Domino(4, 2),
        Domino(1, 0)
    ]

    moves = MoveGenerator.generate(hand, table)

    assert len(moves) == 3

    assert moves[0] == Move(
        placements=[Placement(Domino(6, 6), Side.LEFT)]
    )

    assert moves[1] == Move(
        placements=[Placement(Domino(4, 2), Side.LEFT)]
    )

    assert moves[2] == Move(
        placements=[Placement(Domino(1, 0), Side.LEFT)]
    )


def test_generate_left_moves():
    table = Table()

    table.play(
        Move(
            placements=[Placement(Domino(6, 6), Side.LEFT)]
        )
    )

    table.play(
        Move(
            placements=[Placement(Domino(6, 3), Side.RIGHT)]
        )
    )

    hand = [
        Domino(6, 4),
        Domino(6, 1),
        Domino(2, 2)
    ]

    moves = MoveGenerator.generate(hand, table)

    assert len(moves) == 2

    assert moves[0] == Move(
        placements=[Placement(Domino(6, 4), Side.LEFT)]
    )

    assert moves[1] == Move(
        placements=[Placement(Domino(6, 1), Side.LEFT)]
    )


def test_generate_move_on_both_sides():
    table = Table()

    table.play(
        Move(
            placements=[Placement(Domino(6, 6), Side.LEFT)]
        )
    )

    table.play(
        Move(
            placements=[Placement(Domino(6, 3), Side.RIGHT)]
        )
    )

    hand = [
        Domino(3, 6)
    ]

    moves = MoveGenerator.generate(hand, table)

    assert len(moves) == 2

    assert moves[0] == Move(
        placements=[Placement(Domino(3, 6), Side.LEFT)]
    )

    assert moves[1] == Move(
        placements=[Placement(Domino(3, 6), Side.RIGHT)]
    )


def test_generate_no_moves():
    table = Table()

    table.play(
        Move(
            placements=[Placement(Domino(6, 6), Side.LEFT)]
        )
    )

    table.play(
        Move(
            placements=[Placement(Domino(6, 3), Side.RIGHT)]
        )
    )

    hand = [
        Domino(1, 2),
        Domino(4, 5)
    ]

    moves = MoveGenerator.generate(hand, table)

    assert moves == []


def test_all_generated_moves_are_normal():
    table = Table()

    hand = [
        Domino(6, 6),
        Domino(5, 4)
    ]

    moves = MoveGenerator.generate(hand, table)

    assert len(moves) == 2

    for move in moves:
        assert len(move.placements) == 1
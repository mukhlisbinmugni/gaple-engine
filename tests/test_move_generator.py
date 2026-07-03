from domino import Domino
from move import Move, Side
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
        dominoes=[Domino(6, 6)],
        side=Side.LEFT
    )

    assert moves[1] == Move(
        dominoes=[Domino(4, 2)],
        side=Side.LEFT
    )

    assert moves[2] == Move(
        dominoes=[Domino(1, 0)],
        side=Side.LEFT
    )


def test_generate_left_moves():
    table = Table()

    table.play(
        Move(
            dominoes=[Domino(6, 6)],
            side=Side.LEFT
        )
    )

    table.play(
        Move(
            dominoes=[Domino(6, 3)],
            side=Side.RIGHT
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
        dominoes=[Domino(6, 4)],
        side=Side.LEFT
    )

    assert moves[1] == Move(
        dominoes=[Domino(6, 1)],
        side=Side.LEFT
    )


def test_generate_move_on_both_sides():
    table = Table()

    table.play(
        Move(
            dominoes=[Domino(6, 6)],
            side=Side.LEFT
        )
    )

    table.play(
        Move(
            dominoes=[Domino(6, 3)],
            side=Side.RIGHT
        )
    )

    hand = [
        Domino(3, 6)
    ]

    moves = MoveGenerator.generate(hand, table)

    assert len(moves) == 2

    assert moves[0] == Move(
        dominoes=[Domino(3, 6)],
        side=Side.LEFT
    )

    assert moves[1] == Move(
        dominoes=[Domino(3, 6)],
        side=Side.RIGHT
    )


def test_generate_no_moves():
    table = Table()

    table.play(
        Move(
            dominoes=[Domino(6, 6)],
            side=Side.LEFT
        )
    )

    table.play(
        Move(
            dominoes=[Domino(6, 3)],
            side=Side.RIGHT
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
        assert len(move.dominoes) == 1
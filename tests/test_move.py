import pytest

from domino import Domino
from move import Move, MoveType, Side


def test_default_move_type():
    move = Move(
        dominoes=[Domino(6, 6)],
        side=Side.LEFT
    )

    assert move.move_type == MoveType.NORMAL


def test_move_side():
    move = Move(
        dominoes=[Domino(6, 6)],
        side=Side.RIGHT
    )

    assert move.side == Side.RIGHT


def test_move_contains_one_domino():
    domino = Domino(6, 6)

    move = Move(
        dominoes=[domino],
        side=Side.LEFT
    )

    assert len(move.dominoes) == 1
    assert move.dominoes[0] == domino


def test_ratus_move():
    move = Move(
        dominoes=[
            Domino(2, 2),
            Domino(2, 0)
        ],
        side=Side.LEFT,
        move_type=MoveType.RATUS
    )

    assert move.move_type == MoveType.RATUS
    assert len(move.dominoes) == 2


def test_ribu_move():
    move = Move(
        dominoes=[
            Domino(2, 2),
            Domino(2, 0),
            Domino(0, 0)
        ],
        side=Side.RIGHT,
        move_type=MoveType.RIBU
    )

    assert move.move_type == MoveType.RIBU
    assert len(move.dominoes) == 3


def test_move_string():
    move = Move(
        dominoes=[Domino(6, 6)],
        side=Side.LEFT
    )

    assert str(move) == "NORMAL: [6-6] -> LEFT"


def test_invalid_ribu_move():
    with pytest.raises(ValueError):
        Move(
            dominoes=[Domino(6, 6)],
            side=Side.LEFT,
            move_type=MoveType.RIBU
        )


def test_invalid_ratus_move():
    with pytest.raises(ValueError):
        Move(
            dominoes=[Domino(2, 2)],
            side=Side.LEFT,
            move_type=MoveType.RATUS
        )


def test_invalid_normal_move():
    with pytest.raises(ValueError):
        Move(
            dominoes=[
                Domino(2, 2),
                Domino(2, 0)
            ],
            side=Side.LEFT,
            move_type=MoveType.NORMAL
        )
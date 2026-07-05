import pytest

from domino import Domino
from move import Move, MoveType
from placement import Placement
from side import Side


def test_default_move_type():
    move = Move(
        placements=[Placement(Domino(6, 6), Side.LEFT)]
    )

    assert move.move_type == MoveType.NORMAL


def test_move_placement_side():
    move = Move(
        placements=[Placement(Domino(6, 6), Side.RIGHT)]
    )

    assert move.placements[0].side == Side.RIGHT


def test_move_contains_one_placement():
    domino = Domino(6, 6)

    move = Move(
        placements=[Placement(domino, Side.LEFT)]
    )

    assert len(move.placements) == 1
    assert move.placements[0].domino == domino


def test_ratus_move():
    move = Move(
        placements=[
            Placement(Domino(2, 2), Side.LEFT),
            Placement(Domino(2, 0), Side.RIGHT)
        ],
        move_type=MoveType.RATUS
    )

    assert move.move_type == MoveType.RATUS
    assert len(move.placements) == 2


def test_ribu_move():
    move = Move(
        placements=[
            Placement(Domino(2, 2), Side.RIGHT),
            Placement(Domino(2, 0), Side.RIGHT),
            Placement(Domino(0, 0), Side.RIGHT)
        ],
        move_type=MoveType.RIBU
    )

    assert move.move_type == MoveType.RIBU
    assert len(move.placements) == 3


def test_move_string():
    move = Move(
        placements=[Placement(Domino(6, 6), Side.LEFT)]
    )

    assert str(move) == "NORMAL: 6-6 -> LEFT"


def test_ratus_move_string():
    move = Move(
        placements=[
            Placement(Domino(6, 6), Side.LEFT),
            Placement(Domino(4, 6), Side.RIGHT)
        ],
        move_type=MoveType.RATUS
    )

    assert str(move) == "RATUS: 6-6 -> LEFT, 4-6 -> RIGHT"


def test_invalid_ribu_move():
    with pytest.raises(ValueError):
        Move(
            placements=[Placement(Domino(6, 6), Side.LEFT)],
            move_type=MoveType.RIBU
        )


def test_invalid_ratus_move():
    with pytest.raises(ValueError):
        Move(
            placements=[Placement(Domino(2, 2), Side.LEFT)],
            move_type=MoveType.RATUS
        )


def test_invalid_normal_move():
    with pytest.raises(ValueError):
        Move(
            placements=[
                Placement(Domino(2, 2), Side.LEFT),
                Placement(Domino(2, 0), Side.RIGHT)
            ],
            move_type=MoveType.NORMAL
        )
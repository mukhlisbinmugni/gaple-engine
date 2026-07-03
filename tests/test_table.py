import pytest

from domino import Domino
from move import Move, Side
from table import Table


def test_new_table_is_empty():
    table = Table()

    assert table.is_empty()
    assert table.left_end is None
    assert table.right_end is None


def test_first_move():
    table = Table()

    table.play(
        Move(
            dominoes=[Domino(6, 6)],
            side=Side.LEFT
        )
    )

    assert not table.is_empty()
    assert table.left_end == 6
    assert table.right_end == 6


def test_play_left():
    table = Table()

    table.play(
        Move(
            dominoes=[Domino(6, 6)],
            side=Side.LEFT
        )
    )

    table.play(
        Move(
            dominoes=[Domino(4, 6)],
            side=Side.LEFT
        )
    )

    assert table.left_end == 4
    assert table.right_end == 6


def test_play_right():
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

    assert table.left_end == 6
    assert table.right_end == 3


def test_illegal_move():
    table = Table()

    table.play(
        Move(
            dominoes=[Domino(6, 6)],
            side=Side.LEFT
        )
    )

    with pytest.raises(ValueError):
        table.play(
            Move(
                dominoes=[Domino(5, 4)],
                side=Side.RIGHT
            )
        )


def test_reset_table():
    table = Table()

    table.play(
        Move(
            dominoes=[Domino(6, 6)],
            side=Side.LEFT
        )
    )

    table.reset()

    assert table.is_empty()
    assert table.left_end is None
    assert table.right_end is None


def test_table_string_empty():
    table = Table()

    assert str(table) == "(Meja kosong)"


def test_table_string():
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

    assert str(table) == "6 ...... 3"
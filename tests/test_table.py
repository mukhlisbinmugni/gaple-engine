import pytest

from domino import Domino
from move import Move, MoveType
from placement import Placement
from side import Side
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
            placements=[Placement(Domino(6, 6), Side.LEFT)]
        )
    )

    assert not table.is_empty()
    assert table.left_end == 6
    assert table.right_end == 6


def test_play_left():
    table = Table()

    table.play(
        Move(
            placements=[Placement(Domino(6, 6), Side.LEFT)]
        )
    )

    table.play(
        Move(
            placements=[Placement(Domino(4, 6), Side.LEFT)]
        )
    )

    assert table.left_end == 4
    assert table.right_end == 6


def test_play_right():
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

    assert table.left_end == 6
    assert table.right_end == 3


def test_illegal_move():
    table = Table()

    table.play(
        Move(
            placements=[Placement(Domino(6, 6), Side.LEFT)]
        )
    )

    with pytest.raises(ValueError):
        table.play(
            Move(
                placements=[Placement(Domino(5, 4), Side.RIGHT)]
            )
        )


def test_reset_table():
    table = Table()

    table.play(
        Move(
            placements=[Placement(Domino(6, 6), Side.LEFT)]
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
            placements=[Placement(Domino(6, 6), Side.LEFT)]
        )
    )

    table.play(
        Move(
            placements=[Placement(Domino(6, 3), Side.RIGHT)]
        )
    )

    assert str(table) == "6 ...... 3"


def test_multi_placement_move_applied_sequentially():
    """
    Menguji bahwa Table.play() menerapkan placement satu per satu,
    berurutan -- bukan divalidasi sekaligus di awal. Ini penting
    untuk RATUS nanti, di mana legalitas placement kedua bergantung
    pada state meja setelah placement pertama diterapkan.
    """
    table = Table()

    table.play(
        Move(
            placements=[Placement(Domino(4, 4), Side.LEFT)]
        )
    )

    # Meja: 4....4

    table.play(
        Move(
            placements=[
                # Placement pertama: balak 4-4 di sisi LEFT
                # (sudah cocok dengan ujung 4, tetap 4).
                Placement(Domino(4, 4), Side.LEFT),
                # Placement kedua baru sah SETELAH placement
                # pertama diterapkan; ujung LEFT tetap 4, jadi
                # domino 6-4 di sisi LEFT tetap legal (cocok ke 4).
                Placement(Domino(6, 4), Side.LEFT),
            ],
            move_type=MoveType.RATUS,
        )
    )

    assert table.left_end == 6
    assert table.right_end == 4


def test_previous_ends_recorded_before_whole_move():
    table = Table()

    table.play(
        Move(
            placements=[Placement(Domino(3, 5), Side.LEFT)]
        )
    )

    assert table.previous_left_end is None
    assert table.previous_right_end is None

    table.play(
        Move(
            placements=[Placement(Domino(3, 1), Side.LEFT)]
        )
    )

    # previous_* mencatat state SEBELUM move kedua ini,
    # yaitu hasil dari move pertama (3....5).
    assert table.previous_left_end == 3
    assert table.previous_right_end == 5
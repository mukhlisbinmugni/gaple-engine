from domino import Domino
from move import Move, MoveType
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


# =========================================================
# RATUS
# =========================================================

def _play_normal(table, domino, side):
    table.play(Move(placements=[Placement(domino, side)]))


def test_ratus_generated_when_hand_has_exactly_two_dominoes():
    table = Table()

    _play_normal(table, Domino(5, 4), Side.LEFT)   # ends: 5....4
    _play_normal(table, Domino(4, 6), Side.RIGHT)  # ends: 5....6

    hand = [Domino(5, 5), Domino(6, 5)]

    moves = MoveGenerator.generate(hand, table)

    ratus_moves = [m for m in moves if m.move_type == MoveType.RATUS]

    assert len(ratus_moves) >= 1

    for move in ratus_moves:
        assert len(move.placements) == 2


def test_ratus_not_generated_when_hand_size_is_not_two():
    table = Table()

    _play_normal(table, Domino(5, 4), Side.LEFT)
    _play_normal(table, Domino(4, 6), Side.RIGHT)

    hand = [Domino(5, 5), Domino(6, 5), Domino(1, 1)]

    moves = MoveGenerator.generate(hand, table)

    ratus_moves = [m for m in moves if m.move_type == MoveType.RATUS]

    assert ratus_moves == []


def test_ratus_not_generated_on_empty_table():
    table = Table()

    hand = [Domino(5, 5), Domino(6, 5)]

    moves = MoveGenerator.generate(hand, table)

    ratus_moves = [m for m in moves if m.move_type == MoveType.RATUS]

    assert ratus_moves == []


def test_ratus_move_actually_closes_both_ends():
    """
    Sanity check: setidaknya satu kombinasi RATUS yang dihasilkan,
    kalau benar-benar diterapkan ke Table, menutup kedua ujung
    menjadi sama.
    """
    table = Table()

    _play_normal(table, Domino(5, 4), Side.LEFT)
    _play_normal(table, Domino(4, 6), Side.RIGHT)

    hand = [Domino(5, 5), Domino(6, 5)]

    moves = MoveGenerator.generate(hand, table)
    ratus_moves = [m for m in moves if m.move_type == MoveType.RATUS]

    found_closing_move = False

    for move in ratus_moves:
        scratch = Table()
        scratch.left_end = table.left_end
        scratch.right_end = table.right_end
        scratch.chain = table.chain.copy()

        scratch.play(move)

        if scratch.left_end == scratch.right_end:
            found_closing_move = True
            break

    assert found_closing_move


# =========================================================
# RIBU
# =========================================================

def test_ribu_generated_when_hand_shape_is_correct():
    table = Table()

    _play_normal(table, Domino(5, 4), Side.LEFT)   # ends: 5....4
    _play_normal(table, Domino(4, 2), Side.RIGHT)  # ends: 5....2
    _play_normal(table, Domino(2, 1), Side.RIGHT)  # ends: 5....1
    _play_normal(table, Domino(1, 3), Side.RIGHT)  # ends: 5....3

    hand = [Domino(5, 5), Domino(3, 3), Domino(3, 5)]

    moves = MoveGenerator.generate(hand, table)

    ribu_moves = [m for m in moves if m.move_type == MoveType.RIBU]

    assert len(ribu_moves) >= 1

    for move in ribu_moves:
        assert len(move.placements) == 3


def test_ribu_not_generated_when_no_balak_in_hand():
    """
    Sesuai Contoh 2: meski 3 kartu ini bisa disambung fisik
    berurutan, tidak ada satu pun balak -- RIBU tidak boleh
    ditawarkan sebagai opsi sama sekali.
    """
    table = Table()

    _play_normal(table, Domino(6, 4), Side.LEFT)   # ends: 6....4

    hand = [Domino(6, 2), Domino(2, 4), Domino(4, 1)]

    moves = MoveGenerator.generate(hand, table)

    ribu_moves = [m for m in moves if m.move_type == MoveType.RIBU]

    assert ribu_moves == []


def test_ribu_not_generated_when_only_one_balak():
    """
    Kasus batas: hanya 1 balak (bukan 2) -- bukan bentuk RIBU
    yang sah.
    """
    table = Table()

    _play_normal(table, Domino(5, 4), Side.LEFT)

    hand = [Domino(3, 3), Domino(3, 5), Domino(5, 1)]

    moves = MoveGenerator.generate(hand, table)

    ribu_moves = [m for m in moves if m.move_type == MoveType.RIBU]

    assert ribu_moves == []


def test_ribu_not_generated_on_empty_table():
    table = Table()

    hand = [Domino(5, 5), Domino(3, 3), Domino(3, 5)]

    moves = MoveGenerator.generate(hand, table)

    ribu_moves = [m for m in moves if m.move_type == MoveType.RIBU]

    assert ribu_moves == []
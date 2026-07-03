from game import Game
from domino import Domino
from rule_system import RuleSystem
from game_end_result import FinishType, SpecialResult


def fill_all_players(game):
    """
    Memberikan kartu default agar semua pemain valid, dengan
    total pip yang SENGAJA dibuat berbeda antar pemain agar
    tidak terjadi tie yang tidak disengaja di tie-break DOM.
    Tidak ada domino balak di sini, supaya helper ini netral
    terhadap Step 3.
    """
    default_hands = [
        [Domino(1, 0)],
        [Domino(2, 0)],
        [Domino(3, 0)],
        [Domino(4, 0)],
    ]

    for player, hand in zip(game.players, default_hands):
        player.hand = list(hand)


# =========================================================
# EVALUATE / FINISH TYPE / WINNER (tidak berubah dari sebelumnya)
# =========================================================

def test_rule_system_dom_finish():
    game = Game()

    fill_all_players(game)

    game.players[0].hand = []

    result = RuleSystem.evaluate(game)

    assert result.finish_type == FinishType.DOM


def test_rule_system_detect_winner():
    game = Game()

    fill_all_players(game)

    winner = game.players[2]
    winner.hand = []

    result = RuleSystem.evaluate(game)

    assert result.winner == winner


def test_rule_system_penalty_changes_exist():
    game = Game()

    fill_all_players(game)

    game.players[0].hand = []

    result = RuleSystem.evaluate(game)

    assert isinstance(result.penalty_changes, dict)


def test_rule_system_default_special_result():
    game = Game()

    fill_all_players(game)

    game.players[0].hand = []

    result = RuleSystem.evaluate(game)

    assert result.special_result == SpecialResult.NONE


def test_rule_system_normal_when_no_one_empty():
    game = Game()

    fill_all_players(game)

    result = RuleSystem.evaluate(game)

    assert result.finish_type == FinishType.NORMAL


# =========================================================
# PASAR DETECTION
# =========================================================

def test_rule_system_pasar_when_final_domino_fits_both_ends():
    game = Game()

    fill_all_players(game)

    # Meja: 3 ...... 5 (state sebelum move terakhir)
    game.table.left_end = 3
    game.table.right_end = 5

    # Domino terakhir 5-3 legal di kedua ujung sekaligus.
    winning_domino = Domino(5, 3)

    game.players[0].hand = []
    game.last_move = type(
        "FakeMove", (), {"dominoes": [winning_domino]}
    )()

    game.table.previous_left_end = 3
    game.table.previous_right_end = 5

    result = RuleSystem.evaluate(game)

    assert result.finish_type == FinishType.PASAR


def test_rule_system_dom_when_final_domino_fits_only_one_end():
    game = Game()

    fill_all_players(game)

    game.table.left_end = 3
    game.table.right_end = 5

    # Domino terakhir 5-2 hanya legal di sisi kanan (5),
    # tidak legal di sisi kiri (3).
    winning_domino = Domino(5, 2)

    game.players[0].hand = []
    game.last_move = type(
        "FakeMove", (), {"dominoes": [winning_domino]}
    )()

    game.table.previous_left_end = 3
    game.table.previous_right_end = 5

    result = RuleSystem.evaluate(game)

    assert result.finish_type == FinishType.DOM


def test_rule_system_dom_when_last_move_not_recorded():
    game = Game()

    fill_all_players(game)

    game.players[0].hand = []
    game.last_move = None

    result = RuleSystem.evaluate(game)

    assert result.finish_type == FinishType.DOM


def test_rule_system_dom_when_table_was_empty_before_last_move():
    game = Game()

    fill_all_players(game)

    winning_domino = Domino(6, 6)

    game.players[0].hand = []
    game.last_move = type(
        "FakeMove", (), {"dominoes": [winning_domino]}
    )()

    # Meja masih kosong sebelum move terakhir (move pembuka).
    game.table.previous_left_end = None
    game.table.previous_right_end = None

    result = RuleSystem.evaluate(game)

    assert result.finish_type == FinishType.DOM


# =========================================================
# PLAYER POINTS
# =========================================================

def test_calculate_player_points():
    game = Game()

    game.players[0].hand = [Domino(6, 6)]
    game.players[1].hand = [Domino(5, 4)]
    game.players[2].hand = [Domino(3, 2)]
    game.players[3].hand = [Domino(1, 0)]

    points = RuleSystem.calculate_player_points(game)

    assert points[game.players[0]] == 12
    assert points[game.players[1]] == 9
    assert points[game.players[2]] == 5
    assert points[game.players[3]] == 1


# =========================================================
# DOMINO RANK (sum-based)
# =========================================================

def test_domino_rank_sum_based_ordering():
    # Sum berbeda: sum lebih besar selalu menang,
    # walau angka sisi tunggalnya lebih kecil.
    assert RuleSystem.domino_rank(Domino(5, 4)) > RuleSystem.domino_rank(Domino(6, 0))

    # Sum sama (7): dibandingkan sisi tertinggi.
    assert RuleSystem.domino_rank(Domino(6, 1)) > RuleSystem.domino_rank(Domino(5, 2))

    # Sum dan sisi tertinggi sama tidak mungkin terjadi pada
    # dua domino berbeda dalam satu set, sehingga tidak diuji.

    assert RuleSystem.domino_rank(Domino(6, 6)) > RuleSystem.domino_rank(Domino(6, 5))
    assert RuleSystem.domino_rank(Domino(6, 4)) > RuleSystem.domino_rank(Domino(5, 5))


# =========================================================
# DOM LOSER — STEP 1 (PIP TERBESAR, UNIK)
# =========================================================

def test_find_dom_loser_highest_points():
    game = Game()

    winner = game.players[0]

    game.players[0].hand = []
    game.players[1].hand = [Domino(6, 6)]
    game.players[2].hand = [Domino(5, 4)]
    game.players[3].hand = [Domino(2, 2)]

    points = RuleSystem.calculate_player_points(game)

    loser = RuleSystem.find_dom_loser(points, winner)

    assert loser == game.players[1]


# =========================================================
# DOM LOSER — STEP 2 (JUMLAH KARTU, DENGAN PIP BENAR-BENAR TIED)
# =========================================================

def test_find_dom_loser_more_cards_when_pip_tied():
    game = Game()

    winner = game.players[0]

    game.players[0].hand = []

    # P2 dan P3 sama-sama 8 pip, P2 2 kartu, P3 1 kartu.
    game.players[1].hand = [Domino(6, 1), Domino(1, 0)]  # 7 + 1 = 8
    game.players[2].hand = [Domino(6, 2)]                # 8
    game.players[3].hand = [Domino(1, 1)]                # 2, gugur di Step 1

    points = RuleSystem.calculate_player_points(game)

    loser = RuleSystem.find_dom_loser(points, winner)

    assert loser == game.players[1]


# =========================================================
# DOM LOSER — STEP 3.0 (TEPAT SATU PEMEGANG BALAK)
# =========================================================

def test_find_dom_loser_exactly_one_balak_holder():
    game = Game()

    winner = game.players[0]

    game.players[0].hand = []

    # P1 dan P2 sama-sama 15 pip, 2 kartu. P3 gugur di Step 1.
    game.players[1].hand = [Domino(3, 2), Domino(5, 5)]  # 5 + 10 = 15, balak
    game.players[2].hand = [Domino(4, 1), Domino(6, 4)]  # 5 + 10 = 15, tanpa balak
    game.players[3].hand = [Domino(1, 1)]                # 2

    points = RuleSystem.calculate_player_points(game)

    loser = RuleSystem.find_dom_loser(points, winner)

    assert loser == game.players[1]


# =========================================================
# DOM LOSER — STEP 3a (BALAK GANDA, DIBEDAKAN JUMLAH BALAK)
# =========================================================

def test_find_dom_loser_multiple_balak_resolved_by_balak_count():
    game = Game()

    winner = game.players[0]

    game.players[0].hand = []

    # P1 dan P2 sama-sama 13 pip, 3 kartu, sama-sama pegang balak.
    # P1 pegang 2 balak, P2 pegang 1 balak.
    game.players[1].hand = [Domino(5, 5), Domino(1, 1), Domino(1, 0)]  # 10+2+1=13
    game.players[2].hand = [Domino(4, 4), Domino(2, 0), Domino(3, 0)]  # 8+2+3=13
    game.players[3].hand = [Domino(0, 0)]  # gugur di Step 1

    points = RuleSystem.calculate_player_points(game)

    loser = RuleSystem.find_dom_loser(points, winner)

    assert loser == game.players[1]


# =========================================================
# DOM LOSER — STEP 3b (BALAK GANDA, JUMLAH BALAK JUGA TIED,
# DIBEDAKAN NILAI BALAK TERTINGGI)
# =========================================================

def test_find_dom_loser_multiple_balak_resolved_by_balak_value():
    game = Game()

    winner = game.players[0]

    game.players[0].hand = []

    # P1 dan P2 sama-sama 13 pip, 3 kartu, sama-sama pegang 2 balak.
    # Balak tertinggi P1 = 5-5 (10), balak tertinggi P2 = 4-4 (8).
    game.players[1].hand = [Domino(5, 5), Domino(1, 1), Domino(1, 0)]  # 10+2+1=13
    game.players[2].hand = [Domino(4, 4), Domino(2, 2), Domino(1, 0)]  # 8+4+1=13
    game.players[3].hand = [Domino(0, 0)]

    points = RuleSystem.calculate_player_points(game)

    loser = RuleSystem.find_dom_loser(points, winner)

    assert loser == game.players[1]


# =========================================================
# DOM LOSER — STEP 4 (TIDAK ADA BALAK SAMA SEKALI, SUM-BASED)
# =========================================================

def test_find_dom_loser_step4_sum_based():
    game = Game()

    winner = game.players[0]

    game.players[0].hand = []

    # P1 dan P2 sama-sama 11 pip, 2 kartu, tanpa balak.
    # Domino tertinggi P1 = 6-1 (sum 7), domino tertinggi P2 = 6-2 (sum 8).
    game.players[1].hand = [Domino(6, 1), Domino(4, 0)]  # 7 + 4 = 11
    game.players[2].hand = [Domino(6, 2), Domino(3, 0)]  # 8 + 3 = 11
    game.players[3].hand = [Domino(5, 5)]  # gugur di Step 1

    points = RuleSystem.calculate_player_points(game)

    loser = RuleSystem.find_dom_loser(points, winner)

    assert loser == game.players[2]


def test_find_dom_loser_step4_sum_beats_tile_order():
    game = Game()

    winner = game.players[0]

    game.players[0].hand = []

    # Kasus penegas: metode sum-based HARUS menang atas tile-order.
    # P1 domino tertinggi 6-0 (sum 6). P2 domino tertinggi 5-4 (sum 9).
    # Tile-order lama akan salah memilih P1 (karena 6 > 5),
    # tapi rule yang benar adalah sum-based -> P2 yang dihukum.
    game.players[1].hand = [Domino(6, 0), Domino(5, 0)]  # 6 + 5 = 11
    game.players[2].hand = [Domino(5, 4), Domino(2, 0)]  # 9 + 2 = 11
    game.players[3].hand = [Domino(3, 3)]  # gugur di Step 1

    points = RuleSystem.calculate_player_points(game)

    loser = RuleSystem.find_dom_loser(points, winner)

    assert loser == game.players[2]


# =========================================================
# DOM SCORE
# =========================================================

def test_calculate_dom_score():
    game = Game()

    winner = game.players[0]

    game.players[0].hand = []

    game.players[1].hand = [Domino(6, 6)]
    game.players[2].hand = [Domino(5, 4)]
    game.players[3].hand = [Domino(2, 2)]

    points = RuleSystem.calculate_player_points(game)

    scores = RuleSystem.calculate_dom_score(
        points,
        winner
    )

    assert scores[winner] == -3
    assert scores[game.players[1]] == 3
    assert scores[game.players[2]] == 0
    assert scores[game.players[3]] == 0


def test_calculate_pasar_score():
    game = Game()

    winner = game.players[0]

    game.players[0].hand = []

    game.players[1].hand = [Domino(6, 6)]
    game.players[2].hand = [Domino(5, 4)]
    game.players[3].hand = [Domino(2, 2)]

    points = RuleSystem.calculate_player_points(game)

    scores = RuleSystem.calculate_pasar_score(
        points,
        winner
    )

    assert scores[winner] == -4
    assert scores[game.players[1]] == 4
    assert scores[game.players[2]] == 0
    assert scores[game.players[3]] == 0


def test_calculate_pasar_score_uses_same_tie_break_as_dom():
    # Kasus balak ganda (Step 3b) yang sama seperti test DOM,
    # untuk memastikan PASAR benar-benar memakai ulang tie-break
    # DOM, bukan logika terpisah.
    game = Game()

    winner = game.players[0]

    game.players[0].hand = []

    game.players[1].hand = [Domino(5, 5), Domino(1, 1), Domino(1, 0)]
    game.players[2].hand = [Domino(4, 4), Domino(2, 2), Domino(1, 0)]
    game.players[3].hand = [Domino(0, 0)]

    points = RuleSystem.calculate_player_points(game)

    scores = RuleSystem.calculate_pasar_score(points, winner)

    assert scores[winner] == -4
    assert scores[game.players[1]] == 4
    assert scores[game.players[2]] == 0


def test_rule_system_pasar_evaluate_end_to_end():
    game = Game()

    fill_all_players(game)

    game.table.left_end = 3
    game.table.right_end = 5

    winning_domino = Domino(5, 3)

    game.players[0].hand = []
    game.last_move = type(
        "FakeMove", (), {"dominoes": [winning_domino]}
    )()

    game.table.previous_left_end = 3
    game.table.previous_right_end = 5

    result = RuleSystem.evaluate(game)

    assert result.finish_type == FinishType.PASAR
    assert result.penalty_changes[result.winner] == -4
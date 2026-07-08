from game import Game
from domino import Domino
from move import Move, MoveType
from placement import Placement
from side import Side
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
    game.last_move = Move(
        placements=[Placement(winning_domino, Side.LEFT)]
    )

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
    game.last_move = Move(
        placements=[Placement(winning_domino, Side.LEFT)]
    )

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
    game.last_move = Move(
        placements=[Placement(winning_domino, Side.LEFT)]
    )

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
    game.last_move = Move(
        placements=[Placement(winning_domino, Side.LEFT)]
    )

    game.table.previous_left_end = 3
    game.table.previous_right_end = 5

    result = RuleSystem.evaluate(game)

    assert result.finish_type == FinishType.PASAR
    assert result.penalty_changes[result.winner] == -4


# =========================================================
# GUPLAH DETECTION
# =========================================================

def test_rule_system_guplah_finish_when_blocked_and_no_one_empty():
    game = Game()

    fill_all_players(game)

    game.game_over = True
    game.pass_count = len(game.players)
    game.last_move_player = game.players[0]

    result = RuleSystem.evaluate(game)

    assert result.finish_type == FinishType.GUPLAH


def test_rule_system_normal_when_not_over_and_no_one_empty():
    game = Game()

    fill_all_players(game)

    game.game_over = False

    result = RuleSystem.evaluate(game)

    assert result.finish_type == FinishType.NORMAL


# =========================================================
# GUPLAH WINNER — STEP 1 (PIP TERKECIL, UNIK)
# =========================================================

def test_find_guplah_winner_smallest_pip_unique():
    game = Game()

    game.players[0].hand = [Domino(1, 6), Domino(2, 2)]  # 7+4=11
    game.players[1].hand = [Domino(4, 6), Domino(5, 2)]  # 10+7=17
    game.players[2].hand = [Domino(3, 3), Domino(4, 0)]  # 6+4=10
    game.players[3].hand = [Domino(6, 6)]                # 12

    points = RuleSystem.calculate_player_points(game)

    guplah_maker = game.players[0]

    winner = RuleSystem.find_guplah_winner(points, guplah_maker)

    assert winner == game.players[2]


# =========================================================
# GUPLAH WINNER — OVERRIDE PEMBUAT GUPLAH
# =========================================================

def test_find_guplah_winner_maker_override_when_tied():
    game = Game()

    # P1 dan P2 sama-sama pip 4, tied. P1 adalah pembuat guplah,
    # sehingga dia menang langsung tanpa masuk Step 2/3/4.
    game.players[0].hand = [Domino(2, 2)]  # pip 4
    game.players[1].hand = [Domino(3, 1)]  # pip 4
    game.players[2].hand = [Domino(6, 6)]  # pip 12
    game.players[3].hand = [Domino(5, 5)]  # pip 10

    points = RuleSystem.calculate_player_points(game)

    guplah_maker = game.players[0]

    winner = RuleSystem.find_guplah_winner(points, guplah_maker)

    assert winner == game.players[0]


def test_find_guplah_winner_maker_not_tied_falls_back_to_step2():
    game = Game()

    # P1 dan P3 tied pip terkecil (6), P3 punya kartu lebih
    # sedikit (menang, arah dibalik dari DOM).
    game.players[0].hand = [Domino(4, 1), Domino(1, 0)]  # 5+1=6, 2 kartu
    game.players[1].hand = [Domino(6, 0)]                # 6, 1 kartu
    game.players[2].hand = [Domino(6, 6)]                # 12
    game.players[3].hand = [Domino(6, 6)]                # dummy, akan dioverride

    # Gunakan 3 pemain saja secara efektif: buat P4 gugur jauh.
    game.players[3].hand = [Domino(6, 6), Domino(5, 5)]  # 12+10=22

    # Pembuat guplah adalah P3 (pip 12), bukan bagian dari yang
    # tied pip terkecil (P1=6, P2=6), sehingga override tidak
    # berlaku dan lanjut ke Step 2.
    guplah_maker = game.players[2]

    points = RuleSystem.calculate_player_points(game)

    winner = RuleSystem.find_guplah_winner(points, guplah_maker)

    assert winner == game.players[1]


# =========================================================
# GUPLAH WINNER — STEP 3.0 (SATU PEMAIN BERSIH DARI BALAK)
# =========================================================

def test_find_guplah_winner_exactly_one_clean_player():
    game = Game()

    # P1 punya balak, P2 sama sekali tidak punya domino kembar.
    # Keduanya tied pip 6, tied 2 kartu.
    game.players[0].hand = [Domino(3, 3), Domino(0, 0)]  # 6+0=6, 2 balak
    game.players[1].hand = [Domino(4, 1), Domino(1, 0)]  # 5+1=6, tanpa balak

    game.players[2].hand = [Domino(6, 6)]                # pip 12, gugur di Step 1
    game.players[3].hand = [Domino(5, 5)]                # pip 10, gugur di Step 1

    guplah_maker = game.players[2]  # bukan bagian dari yang tied

    points = RuleSystem.calculate_player_points(game)

    winner = RuleSystem.find_guplah_winner(points, guplah_maker)

    assert winner == game.players[1]


# =========================================================
# GUPLAH WINNER — STEP 3.0 (DUA PEMAIN BERSIH -> LANGSUNG STEP 4)
# =========================================================

def test_find_guplah_winner_multiple_clean_players_skip_to_step4():
    game = Game()

    # P1 dan P2 sama-sama bersih (tanpa balak), P3 pegang balak.
    # Ketiganya tied pip 6, tied 2 kartu.
    game.players[0].hand = [Domino(4, 1), Domino(1, 0)]  # 5+1=6, tanpa balak, tertinggi=4-1(sum5)
    game.players[1].hand = [Domino(3, 1), Domino(2, 0)]  # 4+2=6, tanpa balak, tertinggi=3-1(sum4)
    game.players[2].hand = [Domino(3, 3), Domino(0, 0)]  # 6+0=6, balak

    game.players[3].hand = [Domino(6, 6), Domino(5, 5)]  # gugur di Step 1

    guplah_maker = game.players[3]  # bukan bagian dari yang tied

    points = RuleSystem.calculate_player_points(game)

    winner = RuleSystem.find_guplah_winner(points, guplah_maker)

    # P3 dieliminasi (satu-satunya pemegang balak), lanjut Step 4
    # antara P1 vs P2: sum terendah menang -> P2 (sum 4 < sum 5).
    assert winner == game.players[1]


# =========================================================
# GUPLAH WINNER — STEP 3a (SEMUA PEGANG BALAK, BEDA JUMLAH)
# =========================================================

def test_find_guplah_winner_all_hold_balak_resolved_by_count():
    game = Game()

    # P1 dan P2 tied pip 13, tied 3 kartu, sama-sama pegang balak.
    # P1 pegang 2 balak, P2 pegang 1 balak -> P2 menang (lebih sedikit).
    game.players[0].hand = [Domino(5, 5), Domino(1, 1), Domino(1, 0)]  # 10+2+1=13
    game.players[1].hand = [Domino(4, 4), Domino(2, 0), Domino(3, 0)]  # 8+2+3=13
    game.players[2].hand = [Domino(6, 6), Domino(5, 4)]  # gugur di Step 1
    game.players[3].hand = [Domino(6, 6), Domino(6, 5)]  # gugur di Step 1

    guplah_maker = game.players[2]

    points = RuleSystem.calculate_player_points(game)

    winner = RuleSystem.find_guplah_winner(points, guplah_maker)

    assert winner == game.players[1]


# =========================================================
# GUPLAH WINNER — STEP 3b (SEMUA PEGANG BALAK, JUMLAH SAMA)
# =========================================================

def test_find_guplah_winner_all_hold_balak_resolved_by_value():
    game = Game()

    # P1 dan P2 tied pip 13, tied 3 kartu, sama-sama pegang 2 balak.
    # Balak tertinggi P1 = 5-5 (10), balak tertinggi P2 = 4-4 (8).
    # P2 menang (nilai balak tertinggi lebih rendah).
    game.players[0].hand = [Domino(5, 5), Domino(1, 1), Domino(1, 0)]  # 13
    game.players[1].hand = [Domino(4, 4), Domino(2, 2), Domino(1, 0)]  # 13
    game.players[2].hand = [Domino(6, 6), Domino(5, 4)]
    game.players[3].hand = [Domino(6, 6), Domino(6, 5)]

    guplah_maker = game.players[2]

    points = RuleSystem.calculate_player_points(game)

    winner = RuleSystem.find_guplah_winner(points, guplah_maker)

    assert winner == game.players[1]


# =========================================================
# GUPLAH SCORE — MODE 1: PEMBUAT GUPLAH = WINNER
# =========================================================

def test_calculate_guplah_score_maker_is_winner():
    game = Game()

    game.players[0].hand = [Domino(1, 0)]  # pip 1, winner
    game.players[1].hand = [Domino(4, 6)]  # pip 10
    game.players[2].hand = [Domino(3, 3)]  # pip 6
    game.players[3].hand = [Domino(6, 6)]  # pip 12

    points = RuleSystem.calculate_player_points(game)

    winner = game.players[0]
    guplah_maker = game.players[0]

    scores = RuleSystem.calculate_guplah_score(points, winner, guplah_maker)

    assert scores[game.players[0]] == -5
    assert scores[game.players[1]] == 5
    assert scores[game.players[2]] == 5
    assert scores[game.players[3]] == 5


# =========================================================
# GUPLAH SCORE — MODE 2: PEMBUAT GUPLAH BUKAN WINNER
# =========================================================

def test_calculate_guplah_score_maker_is_not_winner():
    game = Game()

    game.players[0].hand = [Domino(6, 5)]  # pip 11, pembuat guplah, bukan winner
    game.players[1].hand = [Domino(1, 0)]  # pip 1, winner
    game.players[2].hand = [Domino(6, 6)]  # pip 12
    game.players[3].hand = [Domino(5, 5)]  # pip 10

    points = RuleSystem.calculate_player_points(game)

    winner = game.players[1]
    guplah_maker = game.players[0]

    scores = RuleSystem.calculate_guplah_score(points, winner, guplah_maker)

    assert scores[game.players[1]] == -5
    assert scores[game.players[0]] == 5
    assert scores[game.players[2]] == 0
    assert scores[game.players[3]] == 0


def test_rule_system_guplah_evaluate_end_to_end_maker_loses():
    # Pembuat guplah BUKAN winner -> FAILED_GUPLAH.
    game = Game()

    game.players[0].hand = [Domino(6, 5)]  # pembuat guplah, bukan winner
    game.players[1].hand = [Domino(1, 0)]  # winner
    game.players[2].hand = [Domino(6, 6)]
    game.players[3].hand = [Domino(5, 5)]

    game.game_over = True
    game.pass_count = len(game.players)
    game.last_move_player = game.players[0]

    result = RuleSystem.evaluate(game)

    assert result.finish_type == FinishType.GUPLAH
    assert result.special_result == SpecialResult.FAILED_GUPLAH
    assert result.winner == game.players[1]
    assert result.penalty_changes[game.players[1]] == -5
    assert result.penalty_changes[game.players[0]] == 5
    assert result.penalty_changes[game.players[2]] == 0
    assert result.penalty_changes[game.players[3]] == 0


def test_rule_system_guplah_evaluate_end_to_end_maker_wins():
    # Pembuat guplah adalah winner -> SpecialResult.GUPLAH,
    # dan SEMUA pemain lain mendapat +5.
    game = Game()

    game.players[0].hand = [Domino(1, 0)]  # pembuat guplah DAN winner
    game.players[1].hand = [Domino(4, 6)]
    game.players[2].hand = [Domino(3, 3)]
    game.players[3].hand = [Domino(6, 6)]

    game.game_over = True
    game.pass_count = len(game.players)
    game.last_move_player = game.players[0]

    result = RuleSystem.evaluate(game)

    assert result.finish_type == FinishType.GUPLAH
    assert result.special_result == SpecialResult.GUPLAH
    assert result.winner == game.players[0]
    assert result.penalty_changes[game.players[0]] == -5
    assert result.penalty_changes[game.players[1]] == 5
    assert result.penalty_changes[game.players[2]] == 5
    assert result.penalty_changes[game.players[3]] == 5


# =========================================================
# RATUS
# =========================================================

def test_rule_system_ratus_success_end_to_end():
    game = Game()

    maker = game.players[0]
    maker.hand = []

    game.last_move_player = maker
    game.last_move = Move(
        placements=[
            Placement(Domino(5, 5), Side.LEFT),
            Placement(Domino(6, 5), Side.RIGHT),
        ],
        move_type=MoveType.RATUS,
    )

    game.table.left_end = 5
    game.table.right_end = 5

    # Tidak ada pemain lain yang masih pegang mata 5.
    game.players[1].hand = [Domino(1, 0)]
    game.players[2].hand = [Domino(2, 3)]
    game.players[3].hand = [Domino(4, 4)]

    result = RuleSystem.evaluate(game)

    assert result.finish_type == FinishType.RATUS
    assert result.special_result == SpecialResult.RATUS
    assert result.winner == maker
    assert result.penalty_changes[maker] == -50
    assert result.penalty_changes[game.players[1]] == 50
    assert result.penalty_changes[game.players[2]] == 50
    assert result.penalty_changes[game.players[3]] == 50


def test_rule_system_ratus_failed_due_to_wrong_shape():
    game = Game()

    maker = game.players[0]
    maker.hand = []

    game.last_move_player = maker
    game.last_move = Move(
        placements=[
            Placement(Domino(5, 5), Side.LEFT),
            Placement(Domino(6, 5), Side.RIGHT),
        ],
        move_type=MoveType.RATUS,
    )

    # Ujung meja TIDAK sama -> gagal karena bentuk, terlepas dari
    # apakah kartu sudah habis atau belum.
    game.table.left_end = 4
    game.table.right_end = 2

    game.players[1].hand = [Domino(1, 0)]
    game.players[2].hand = [Domino(2, 3)]
    game.players[3].hand = [Domino(4, 4)]

    result = RuleSystem.evaluate(game)

    assert result.finish_type == FinishType.RATUS
    assert result.special_result == SpecialResult.FAILED_RATUS
    assert result.winner is None
    assert result.penalty_changes[maker] == 15
    assert result.penalty_changes[game.players[1]] == 0
    assert result.penalty_changes[game.players[2]] == 0
    assert result.penalty_changes[game.players[3]] == 0


def test_rule_system_ratus_failed_because_value_not_exhausted():
    game = Game()

    maker = game.players[0]
    maker.hand = []

    game.last_move_player = maker
    game.last_move = Move(
        placements=[
            Placement(Domino(5, 5), Side.LEFT),
            Placement(Domino(6, 5), Side.RIGHT),
        ],
        move_type=MoveType.RATUS,
    )

    # Bentuk benar (kedua ujung sama = 5), TAPI masih ada mata 5
    # di tangan pemain lain -> gagal.
    game.table.left_end = 5
    game.table.right_end = 5

    game.players[1].hand = [Domino(5, 2)]
    game.players[2].hand = [Domino(2, 3)]
    game.players[3].hand = [Domino(4, 4)]

    result = RuleSystem.evaluate(game)

    assert result.finish_type == FinishType.RATUS
    assert result.special_result == SpecialResult.FAILED_RATUS
    assert result.winner is None
    assert result.penalty_changes[maker] == 15
    assert result.penalty_changes[game.players[1]] == 0


# =========================================================
# RIBU
# =========================================================

def test_rule_system_ribu_success_end_to_end():
    game = Game()

    maker = game.players[0]
    maker.hand = []

    game.last_move_player = maker
    game.last_move = Move(
        placements=[
            Placement(Domino(3, 3), Side.LEFT),
            Placement(Domino(3, 5), Side.LEFT),
            Placement(Domino(5, 5), Side.LEFT),
        ],
        move_type=MoveType.RIBU,
    )

    game.table.left_end = 5
    game.table.right_end = 5

    # Tidak ada pemain lain yang masih pegang mata 3 ATAU 5.
    game.players[1].hand = [Domino(1, 0)]
    game.players[2].hand = [Domino(2, 4)]
    game.players[3].hand = [Domino(6, 6)]

    result = RuleSystem.evaluate(game)

    assert result.finish_type == FinishType.RIBU
    assert result.special_result == SpecialResult.RIBU
    assert result.winner == maker
    assert result.penalty_changes[maker] == -50
    assert result.penalty_changes[game.players[1]] == 20
    assert result.penalty_changes[game.players[2]] == 20
    assert result.penalty_changes[game.players[3]] == 20


def test_rule_system_ribu_failed_due_to_wrong_shape():
    game = Game()

    maker = game.players[0]
    maker.hand = []

    game.last_move_player = maker
    game.last_move = Move(
        placements=[
            Placement(Domino(3, 3), Side.LEFT),
            Placement(Domino(3, 5), Side.LEFT),
            Placement(Domino(5, 5), Side.LEFT),
        ],
        move_type=MoveType.RIBU,
    )

    # Ujung meja TIDAK sama -> gagal karena bentuk.
    game.table.left_end = 5
    game.table.right_end = 2

    game.players[1].hand = [Domino(1, 0)]
    game.players[2].hand = [Domino(2, 4)]
    game.players[3].hand = [Domino(6, 6)]

    result = RuleSystem.evaluate(game)

    assert result.finish_type == FinishType.RIBU
    assert result.special_result == SpecialResult.FAILED_RIBU
    assert result.winner is None
    assert result.penalty_changes[maker] == 25
    assert result.penalty_changes[game.players[1]] == 0


def test_rule_system_ribu_failed_because_value_not_exhausted():
    game = Game()

    maker = game.players[0]
    maker.hand = []

    game.last_move_player = maker
    game.last_move = Move(
        placements=[
            Placement(Domino(3, 3), Side.LEFT),
            Placement(Domino(3, 5), Side.LEFT),
            Placement(Domino(5, 5), Side.LEFT),
        ],
        move_type=MoveType.RIBU,
    )

    game.table.left_end = 5
    game.table.right_end = 5

    # Bentuk benar, TAPI masih ada mata 3 di tangan pemain lain.
    game.players[1].hand = [Domino(3, 0)]
    game.players[2].hand = [Domino(2, 4)]
    game.players[3].hand = [Domino(6, 6)]

    result = RuleSystem.evaluate(game)

    assert result.finish_type == FinishType.RIBU
    assert result.special_result == SpecialResult.FAILED_RIBU
    assert result.winner is None
    assert result.penalty_changes[maker] == 25
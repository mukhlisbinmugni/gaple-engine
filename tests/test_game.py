from domino import Domino
from move import Move, MoveType
from placement import Placement
from side import Side
from game import Game
from turn_result import TurnStatus


def test_new_game():
    game = Game()

    assert len(game.players) == 4
    assert game.active_player().name == "P1"
    assert game.table.is_empty()


def test_start_game():
    game = Game()

    game.start()

    for player in game.players:
        assert len(player.hand) == 7

    assert len(game.deck.cards) == 0


def test_active_player():
    game = Game()

    assert game.active_player().name == "P1"


def test_next_turn():
    game = Game()

    assert game.active_player().name == "P1"

    game.next_turn()
    assert game.active_player().name == "P2"

    game.next_turn()
    assert game.active_player().name == "P3"

    game.next_turn()
    assert game.active_player().name == "Mukhlis"

    game.next_turn()
    assert game.active_player().name == "P1"


def test_choose_move():
    game = Game()

    moves = [
        Move(
            placements=[Placement(Domino(6, 6), Side.LEFT)]
        ),
        Move(
            placements=[Placement(Domino(6, 5), Side.RIGHT)]
        )
    ]

    chosen = game.choose_move(moves)

    # Default chooser sekarang memilih ACAK di antara move NORMAL,
    # jadi kita cek keanggotaan, bukan kesamaan persis dengan
    # moves[0].
    assert chosen in moves


def test_choose_move_prioritizes_ratus_over_normal():
    game = Game()

    normal_move = Move(
        placements=[Placement(Domino(6, 6), Side.LEFT)]
    )
    ratus_move = Move(
        placements=[
            Placement(Domino(5, 5), Side.LEFT),
            Placement(Domino(6, 5), Side.RIGHT),
        ],
        move_type=MoveType.RATUS,
    )

    moves = [normal_move, ratus_move]

    # Dijalankan berulang kali supaya tidak kebetulan lolos --
    # RATUS harus SELALU dipilih setiap kali, bukan cuma sesekali.
    for _ in range(20):
        chosen = game.choose_move(moves)
        assert chosen == ratus_move


def test_set_move_chooser_overrides_single_player():
    game = Game()

    fixed_move = Move(
        placements=[Placement(Domino(1, 1), Side.LEFT)]
    )

    def always_pick_first(moves):
        return fixed_move

    game.set_move_chooser(0, always_pick_first)

    other_move = Move(
        placements=[Placement(Domino(2, 2), Side.LEFT)]
    )

    # Pemain index 0 memakai chooser kustom.
    game.current_player = 0
    assert game.choose_move([other_move]) == fixed_move

    # Pemain lain TIDAK terpengaruh, tetap pakai default chooser.
    game.current_player = 1
    assert game.choose_move([other_move]) == other_move


def test_play_turn_play():
    game = Game()

    game.players[0].hand = [
        Domino(6, 6)
    ]

    result = game.play_turn()

    assert result.status == TurnStatus.PLAY
    assert game.table.left_end == 6
    assert game.table.right_end == 6
    assert game.players[0].is_empty()

    # Game langsung selesai karena pemain menghabiskan kartu.
    assert game.is_over() is True

    # Turn tidak berpindah setelah game selesai.
    assert game.active_player().name == "P1"


def test_play_turn_pass():
    game = Game()

    game.table.play(
        Move(
            placements=[Placement(Domino(6, 6), Side.LEFT)]
        )
    )

    game.table.play(
        Move(
            placements=[Placement(Domino(6, 3), Side.RIGHT)]
        )
    )

    game.players[0].hand = [
        Domino(1, 1),
        Domino(2, 2)
    ]

    result = game.play_turn()

    assert result.status == TurnStatus.PASS
    assert game.active_player().name == "P2"


def test_game_over_after_last_card():
    game = Game()

    player = game.players[0]

    player.hand = [
        Domino(6, 6)
    ]

    game.play_turn()

    assert game.is_over() is True


def test_pass_increases_pass_count():
    game = Game()

    game.table.play(
        Move(
            placements=[Placement(Domino(6, 6), Side.LEFT)]
        )
    )

    game.table.play(
        Move(
            placements=[Placement(Domino(6, 3), Side.RIGHT)]
        )
    )

    game.players[0].hand = [
        Domino(1, 1)
    ]

    game.play_turn()

    assert game.pass_count == 1


def test_play_resets_pass_count():
    game = Game()

    game.pass_count = 3

    game.players[0].hand = [
        Domino(6, 6)
    ]

    game.play_turn()

    assert game.pass_count == 0


def test_four_consecutive_passes_end_game():
    game = Game()

    game.table.play(
        Move(
            placements=[Placement(Domino(6, 6), Side.LEFT)]
        )
    )

    game.table.play(
        Move(
            placements=[Placement(Domino(6, 3), Side.RIGHT)]
        )
    )

    for player in game.players:
        player.hand = [
            Domino(1, 1)
        ]

    for _ in range(4):
        game.play_turn()

    assert game.is_over() is True
    assert game.pass_count == 4


def test_last_move_player_recorded_on_play():
    game = Game()

    game.players[0].hand = [
        Domino(6, 6)
    ]

    game.play_turn()

    assert game.last_move_player == game.players[0]
    assert game.last_move.placements[0].domino == Domino(6, 6)
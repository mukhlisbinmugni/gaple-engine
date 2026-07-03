from domino import Domino
from move import Move, Side
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
            dominoes=[Domino(6, 6)],
            side=Side.LEFT
        ),
        Move(
            dominoes=[Domino(6, 5)],
            side=Side.RIGHT
        )
    ]

    chosen = game.choose_move(moves)

    assert chosen == moves[0]


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
            dominoes=[Domino(6, 6)],
            side=Side.LEFT
        )
    )

    game.table.play(
        Move(
            dominoes=[Domino(6, 3)],
            side=Side.RIGHT
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
            dominoes=[Domino(6, 6)],
            side=Side.LEFT
        )
    )

    game.table.play(
        Move(
            dominoes=[Domino(6, 3)],
            side=Side.RIGHT
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
            dominoes=[Domino(6, 6)],
            side=Side.LEFT
        )
    )

    game.table.play(
        Move(
            dominoes=[Domino(6, 3)],
            side=Side.RIGHT
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
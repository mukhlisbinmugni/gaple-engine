from player import Player
from domino import Domino


def test_draw_card():
    player = Player("Mukhlis")

    card = Domino(6, 6)

    player.draw(card)

    assert player.has_card(card)


def test_play_card():
    player = Player("Mukhlis")

    card = Domino(6, 6)

    player.draw(card)

    played = player.play(card)

    assert played == card
    assert not player.has_card(card)


def test_is_empty():
    player = Player("Mukhlis")

    assert player.is_empty()

    player.draw(Domino(1, 2))

    assert not player.is_empty()

    player.play(Domino(1, 2))

    assert player.is_empty()


def test_total_pips():
    player = Player("Mukhlis")

    player.draw(Domino(6, 6))
    player.draw(Domino(6, 4))

    assert player.total_pips() == 22


def test_has_playable_card():
    player = Player("Mukhlis")

    player.draw(Domino(6, 4))
    player.draw(Domino(2, 1))

    assert player.has_playable_card(6, 3)
    assert player.has_playable_card(0, 1)
    assert not player.has_playable_card(5, 3)
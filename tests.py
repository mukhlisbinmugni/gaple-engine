from deck import Deck
from player import Player
from domino import Domino


def test_deck():
    deck = Deck()

    # Harus ada 28 kartu
    assert len(deck.cards) == 28

    # Shuffle tidak mengubah jumlah kartu
    deck.shuffle()
    assert len(deck.cards) == 28

    # Bagikan ke 4 pemain
    hands = deck.deal()

    assert len(hands) == 4

    # Setiap pemain mendapat 7 kartu
    for hand in hands:
        assert len(hand) == 7

    # Setelah dibagikan tidak ada kartu tersisa
    assert len(deck.cards) == 0

    print("✅ Semua test Deck berhasil!")


def test_player():
    player = Player()

    assert player.is_empty()

    card1 = Domino(2, 5)
    card2 = Domino(6, 6)

    player.draw(card1)
    player.draw(card2)

    assert not player.is_empty()
    assert player.has_card(card1)
    assert player.total_pips() == 19

    assert player.has_playable_card(5, 1)
    assert player.has_playable_card(3, 6)
    assert not player.has_playable_card(0, 4)

    played = player.play(card1)

    assert played == card1
    assert not player.has_card(card1)

    print("✅ Semua test Player berhasil!")


if __name__ == "__main__":
    print("TEST DIMULAI")

    test_deck()
    test_player()
print("TEST DIMULAI")
from deck import Deck


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


if __name__ == "__main__":
    test_deck()
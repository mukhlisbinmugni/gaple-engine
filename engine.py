from deck import Deck
from player import Player


class GapleEngine:
    """
    Engine utama permainan Gaple.
    Bertanggung jawab mengatur jalannya permainan,
    bukan logika kartu.
    """

    def __init__(self):
        self.deck = None
        self.players = []
        self.current_turn = 0

    def new_game(self):
        """Memulai permainan baru."""

        self.deck = Deck()
        self.deck.shuffle()

        self.players = [
            Player("P1"),
            Player("P2"),
            Player("P3"),
            Player("Mukhlis")
        ]

        hands = self.deck.deal()

        for player, hand in zip(self.players, hands):
            for card in hand:
                player.draw(card)

        self.current_turn = 0

    def show_hands(self):
        print("=== Kartu Pemain ===")

        for player in self.players:
            print(player.name)
            print(sorted(player.hand, key=lambda c: (c.left, c.right)))
            print()

        print("Sisa kartu di deck :", len(self.deck.cards))


if __name__ == "__main__":
    engine = GapleEngine()
    engine.new_game()
    engine.show_hands()
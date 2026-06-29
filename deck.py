from domino import Domino
import random


class Deck:
    def __init__(self):
        self.cards = [
            Domino(i, j)
            for i in range(7)
            for j in range(i, 7)
        ]

    def shuffle(self):
        random.shuffle(self.cards)

    def deal(self, players=4, cards_each=7):
        if players * cards_each > len(self.cards):
            raise ValueError("Jumlah kartu tidak mencukupi.")

        hands = []

        for _ in range(players):
            hand = []
            for _ in range(cards_each):
                hand.append(self.cards.pop())
            hands.append(hand)

        return hands
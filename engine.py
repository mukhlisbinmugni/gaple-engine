"""
Gaple Engine
Version : 0.1
Author  : Mukhlis & ChatGPT

Tahap pertama:
- Membuat deck domino
- Mengocok kartu
- Membagikan kartu
"""

import random


class GapleEngine:

    def __init__(self):
        self.deck = []
        self.players = {
            "P1": [],
            "P2": [],
            "P3": [],
            "Mukhlis": []
        }

    def create_deck(self):
        self.deck = []

        for i in range(7):
            for j in range(i, 7):
                self.deck.append((i, j))

    def shuffle_deck(self):
        random.shuffle(self.deck)

    def deal_cards(self):
        for player in self.players:
            self.players[player] = []

        for _ in range(7):
            for player in self.players:
                self.players[player].append(self.deck.pop())

    def show_cards(self):
        print("=== Kartu Pemain ===")

        for player in self.players:
            print(player)
            print(sorted(self.players[player]))
            print()

        print("Sisa kartu di deck :", len(self.deck))


engine = GapleEngine()

engine.create_deck()
engine.shuffle_deck()
engine.deal_cards()
engine.show_cards()

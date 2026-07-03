from domino import Domino


class Player:
    """
    Merepresentasikan satu pemain Gaple.
    Bertanggung jawab mengelola kartu yang dimiliki pemain.
    """

    def __init__(self, name: str):
        self.name = name
        self.hand = []

    def __str__(self):
        return self.name

    def draw(self, card: Domino):
        """Menambahkan kartu ke tangan pemain."""
        self.hand.append(card)

    def has_card(self, card: Domino) -> bool:
        """Apakah pemain memiliki kartu tertentu?"""
        return card in self.hand

    def play(self, card: Domino) -> Domino:
        """
        Mengeluarkan kartu dari tangan pemain.
        Mengembalikan kartu yang dimainkan.
        """
        if card not in self.hand:
            raise ValueError(f"{self.name} tidak memiliki kartu {card}")

        self.hand.remove(card)
        return card

    def is_empty(self) -> bool:
        """Apakah semua kartu pemain sudah habis?"""
        return len(self.hand) == 0

    def total_pips(self) -> int:
        """Menghitung total nilai semua kartu yang masih dipegang."""
        return sum(card.left + card.right for card in self.hand)

    def has_playable_card(self, left_end: int, right_end: int) -> bool:
        """Apakah pemain memiliki minimal satu kartu yang bisa dimainkan?"""
        return any(
            card.can_connect(left_end) or card.can_connect(right_end)
            for card in self.hand
        )
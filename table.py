from domino import Domino
from move import Side, Move
from placed_domino import PlacedDomino


class Table:
    """
    Merepresentasikan keadaan meja permainan Gaple.
    """

    def __init__(self):
        self.chain = []
        self.left_end = None
        self.right_end = None

        # Mencatat ujung meja SEBELUM move terakhir diterapkan.
        # Fakta ini dibutuhkan oleh RuleSystem untuk mendeteksi
        # PASAR (domino terakhir legal di kedua ujung meja
        # sekaligus). Table hanya mencatat fakta ini, tidak
        # menafsirkannya.
        self.previous_left_end = None
        self.previous_right_end = None

    def reset(self):
        self.chain.clear()
        self.left_end = None
        self.right_end = None
        self.previous_left_end = None
        self.previous_right_end = None

    def is_empty(self) -> bool:
        return len(self.chain) == 0

    def can_play(self, domino: Domino, side: Side) -> bool:
        if self.is_empty():
            return True

        if side == Side.LEFT:
            return domino.can_connect(self.left_end)

        if side == Side.RIGHT:
            return domino.can_connect(self.right_end)

        return False

    def play(self, move: Move):
        """
        Menjalankan satu langkah permainan Gaple.
        """

        domino = move.dominoes[0]

        # 1. validasi
        if not self.can_play(domino, move.side):
            raise ValueError(f"Move tidak valid: {domino} ke {move.side}")

        # Catat ujung meja sebelum move ini diterapkan.
        self.previous_left_end = self.left_end
        self.previous_right_end = self.right_end

        # 2. meja kosong
        if self.is_empty():
            self.chain.append(
                PlacedDomino(domino, domino.left, domino.right)
            )
            self.left_end = domino.left
            self.right_end = domino.right
            return

        # 3. LEFT
        if move.side == Side.LEFT:
            if domino.right == self.left_end:
                outward = domino.left
                inward = domino.right
            else:
                outward = domino.right
                inward = domino.left

            self.chain.insert(0, PlacedDomino(domino, outward, inward))
            self.left_end = outward

        # 4. RIGHT
        elif move.side == Side.RIGHT:
            if domino.left == self.right_end:
                outward = domino.right
                inward = domino.left
            else:
                outward = domino.left
                inward = domino.right

            self.chain.append(PlacedDomino(domino, outward, inward))
            self.right_end = outward

    def __str__(self):
        if self.is_empty():
            return "(Meja kosong)"

        return f"{self.left_end} ...... {self.right_end}"
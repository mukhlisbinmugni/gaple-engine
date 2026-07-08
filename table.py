from domino import Domino
from move import Move
from side import Side
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
        Menjalankan satu Move, yang dapat terdiri dari satu atau
        lebih Placement (mis. RATUS = 2 placement, RIBU = 3
        placement dalam 1 Move).

        Move bersifat ATOMIK: setiap placement diterapkan satu per
        satu secara berurutan (karena legalitas placement berikutnya
        bisa bergantung pada state hasil placement sebelumnya dalam
        Move yang sama), tetapi jika SATU SAJA placement gagal,
        SELURUH move dibatalkan -- meja dikembalikan persis seperti
        sebelum Move ini mulai diterapkan. Tidak boleh ada state
        "setengah jadi" yang tertinggal.
        """

        chain_snapshot = self.chain.copy()
        left_end_snapshot = self.left_end
        right_end_snapshot = self.right_end

        for placement in move.placements:
            try:
                self._apply_placement(placement.domino, placement.side)
            except ValueError:
                # Rollback penuh: seolah-olah Move ini tidak pernah
                # terjadi sama sekali.
                self.chain = chain_snapshot
                self.left_end = left_end_snapshot
                self.right_end = right_end_snapshot
                raise

        # Move berhasil sepenuhnya -- baru sekarang catat ujung
        # meja SEBELUM move ini sebagai previous_*. Jika move gagal
        # (branch di atas), previous_* sengaja TIDAK diubah, karena
        # move yang gagal dianggap tidak pernah terjadi.
        self.previous_left_end = left_end_snapshot
        self.previous_right_end = right_end_snapshot

    def _apply_placement(self, domino: Domino, side: Side):
        """
        Menerapkan SATU placement (satu domino, satu sisi) ke meja.
        Ini adalah logika yang sebelumnya berada langsung di play(),
        sekarang diekstrak agar bisa dipanggil berulang untuk Move
        yang berisi lebih dari satu placement.
        """

        if not self.can_play(domino, side):
            raise ValueError(f"Move tidak valid: {domino} ke {side}")

        # meja kosong
        if self.is_empty():
            self.chain.append(
                PlacedDomino(domino, domino.left, domino.right)
            )
            self.left_end = domino.left
            self.right_end = domino.right
            return

        # LEFT
        if side == Side.LEFT:
            if domino.right == self.left_end:
                outward = domino.left
                inward = domino.right
            else:
                outward = domino.right
                inward = domino.left

            self.chain.insert(0, PlacedDomino(domino, outward, inward))
            self.left_end = outward

        # RIGHT
        elif side == Side.RIGHT:
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

    @staticmethod
    def simulate_placement(left_end: int, right_end: int, domino: Domino, side: Side):
        """
        Mensimulasikan SATU placement secara murni (tanpa efek
        samping ke Table manapun), mengembalikan (new_left, new_right)
        jika legal, atau None jika tidak legal.

        Dipakai oleh MoveGenerator untuk mencoba berbagai kombinasi
        urutan+sisi untuk RATUS/RIBU tanpa perlu mengubah Table asli
        atau membuat salinan Table. Logikanya sengaja disalin dari
        _apply_placement (bagian LEFT/RIGHT saja -- kasus meja kosong
        tidak relevan di sini karena RATUS/RIBU hanya mungkin terjadi
        setelah beberapa giliran, sehingga meja tidak pernah kosong).
        """

        if side == Side.LEFT:
            if not domino.can_connect(left_end):
                return None

            if domino.right == left_end:
                outward = domino.left
            else:
                outward = domino.right

            return (outward, right_end)

        if side == Side.RIGHT:
            if not domino.can_connect(right_end):
                return None

            if domino.left == right_end:
                outward = domino.right
            else:
                outward = domino.left

            return (left_end, outward)

        return None
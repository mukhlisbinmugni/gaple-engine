from itertools import permutations, product

from move import Move, MoveType
from placement import Placement
from side import Side
from domino import Domino
from table import Table


class MoveGenerator:
    """
    Menghasilkan seluruh Move yang legal dari tangan pemain.
    """

    @staticmethod
    def generate(hand: list[Domino], table: Table) -> list[Move]:
        moves = []

        for domino in hand:

            # Jika meja masih kosong,
            # cukup hasilkan satu move.
            if table.is_empty():
                moves.append(
                    Move(
                        placements=[Placement(domino, Side.LEFT)]
                    )
                )
                continue

            # LEFT move
            if table.can_play(domino, Side.LEFT):
                moves.append(
                    Move(
                        placements=[Placement(domino, Side.LEFT)]
                    )
                )

            # RIGHT move
            if table.can_play(domino, Side.RIGHT):
                moves.append(
                    Move(
                        placements=[Placement(domino, Side.RIGHT)]
                    )
                )

        # RATUS dan RIBU hanya mungkin terjadi setelah beberapa
        # giliran (meja tidak kosong), dan hanya jika sisa tangan
        # pemain PERSIS 2 (RATUS) atau 3 (RIBU) kartu -- karena
        # keduanya wajib menghabiskan seluruh sisa tangan.
        if not table.is_empty():
            if len(hand) == 2:
                moves.extend(MoveGenerator._generate_ratus(hand, table))
            elif len(hand) == 3:
                moves.extend(MoveGenerator._generate_ribu(hand, table))

        return moves

    @staticmethod
    def _generate_ratus(hand: list[Domino], table: Table) -> list[Move]:
        """
        RATUS tidak mensyaratkan bentuk tangan tertentu (tidak
        harus balak+penghubung) -- MoveGenerator hanya mengecek
        apakah kedua kartu terakhir bisa disambung secara legal,
        berapa pun hasil akhirnya. RuleSystem yang menentukan
        sukses/gagal setelah move ini benar-benar dimainkan.
        """
        return MoveGenerator._generate_multi_placement_moves(
            hand, table, MoveType.RATUS
        )

    @staticmethod
    def _generate_ribu(hand: list[Domino], table: Table) -> list[Move]:
        """
        RIBU MENSYARATKAN bentuk tangan yang spesifik: tepat 2
        domino balak (dengan nilai berbeda) dan 1 domino penghubung
        yang menyambungkan kedua nilai balak tersebut. Jika bentuk
        tangan tidak seperti ini, RIBU tidak pernah ditawarkan
        sebagai opsi sama sekali -- ketiga kartu itu tetap bisa
        dimainkan satu per satu sebagai NORMAL.
        """

        balak = [d for d in hand if d.left == d.right]
        non_balak = [d for d in hand if d.left != d.right]

        if len(balak) != 2 or len(non_balak) != 1:
            return []

        connector = non_balak[0]
        balak_values = {balak[0].left, balak[1].left}
        connector_values = {connector.left, connector.right}

        if balak_values != connector_values:
            return []

        return MoveGenerator._generate_multi_placement_moves(
            hand, table, MoveType.RIBU
        )

    @staticmethod
    def _generate_multi_placement_moves(
        dominoes: list[Domino], table: Table, move_type: MoveType
    ) -> list[Move]:
        """
        Mencoba SEMUA kombinasi urutan dan sisi (LEFT/RIGHT) dari
        sekumpulan domino, memakai Table.simulate_placement (murni,
        tanpa efek samping) untuk mengecek legalitas setiap langkah
        secara berurutan. Setiap kombinasi yang seluruhnya legal
        menghasilkan satu Move kandidat.

        Fungsi ini generik -- dipakai baik oleh RATUS (2 domino)
        maupun RIBU (3 domino), sehingga logika pencarian kombinasi
        tidak perlu diduplikasi.
        """

        moves = []
        seen = set()

        for order in permutations(dominoes):
            for sides in product([Side.LEFT, Side.RIGHT], repeat=len(order)):

                current_left = table.left_end
                current_right = table.right_end
                placements = []
                valid = True

                for domino, side in zip(order, sides):
                    result = Table.simulate_placement(
                        current_left, current_right, domino, side
                    )

                    if result is None:
                        valid = False
                        break

                    current_left, current_right = result
                    placements.append(Placement(domino, side))

                if not valid:
                    continue

                key = tuple((p.domino, p.side) for p in placements)

                if key in seen:
                    continue

                seen.add(key)
                moves.append(
                    Move(placements=placements, move_type=move_type)
                )

        return moves
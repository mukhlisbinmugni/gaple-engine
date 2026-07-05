from move import Move
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

        return moves
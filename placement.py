from dataclasses import dataclass

from domino import Domino
from side import Side


@dataclass(frozen=True)
class Placement:
    """
    Merepresentasikan SATU penempatan domino sebagai bagian dari
    sebuah Move.

    Placement adalah instruksi SEBELUM diterapkan ke meja:
    "domino ini, dituju ke sisi ini."

    Ini berbeda dari PlacedDomino (di placed_domino.py), yang
    merupakan catatan fakta SETELAH domino diterapkan ke chain
    meja (menyimpan outward/inward hasil perhitungan Table).
    Placement adalah bagian dari Move; PlacedDomino adalah bagian
    dari Table.chain. Keduanya menjawab pertanyaan yang berbeda
    dan tidak saling menggantikan.

    domino : kartu yang akan dimainkan
    side   : sisi meja yang dituju untuk domino ini
    """

    domino: Domino
    side: Side

    def __str__(self):
        return f"{self.domino.left}-{self.domino.right} -> {self.side.name}"
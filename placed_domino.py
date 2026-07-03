from dataclasses import dataclass

from domino import Domino


@dataclass(frozen=True)
class PlacedDomino:
    """
    Merepresentasikan sebuah kartu yang sudah diletakkan di meja.

    domino   : kartu aslinya
    outward  : angka yang menghadap ke luar (ujung meja)
    inward   : angka yang menempel dengan rantai meja
    """

    domino: Domino
    outward: int
    inward: int

    def __str__(self):
        return f"{self.outward}-{self.inward}"
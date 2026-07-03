from dataclasses import dataclass
from enum import Enum, auto

from domino import Domino


class Side(Enum):
    """
    Sisi meja tempat kartu dimainkan.
    """
    LEFT = auto()
    RIGHT = auto()


class MoveType(Enum):
    """
    Jenis langkah yang dilakukan pemain.
    """
    NORMAL = auto()
    RATUS = auto()
    RIBU = auto()


@dataclass(frozen=True)
class Move:
    """
    Merepresentasikan satu aksi yang dilakukan pemain.

    dominoes  : daftar kartu yang dimainkan
                - NORMAL -> 1 kartu
                - RATUS  -> 2 kartu
                - RIBU   -> 3 kartu

    side      : sisi meja tempat aksi dilakukan

    move_type : jenis langkah
    """

    dominoes: list[Domino]
    side: Side
    move_type: MoveType = MoveType.NORMAL

    def __post_init__(self):
        """
        Memastikan jumlah kartu sesuai dengan jenis Move.
        """

        expected = {
            MoveType.NORMAL: 1,
            MoveType.RATUS: 2,
            MoveType.RIBU: 3,
        }

        required = expected[self.move_type]

        if len(self.dominoes) != required:
            raise ValueError(
                f"{self.move_type.name} requires exactly {required} domino(es)."
            )

    def __str__(self):
        cards = ", ".join(str(domino) for domino in self.dominoes)
        return f"{self.move_type.name}: [{cards}] -> {self.side.name}"
from dataclasses import dataclass
from enum import Enum, auto

from placement import Placement


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

    placements : daftar Placement yang dilakukan dalam satu Move
                 - NORMAL -> 1 placement
                 - RATUS  -> 2 placement
                 - RIBU   -> 3 placement

    move_type  : jenis langkah
    """

    placements: list[Placement]
    move_type: MoveType = MoveType.NORMAL

    def __post_init__(self):
        """
        Memastikan jumlah placement sesuai dengan jenis Move.
        """

        expected = {
            MoveType.NORMAL: 1,
            MoveType.RATUS: 2,
            MoveType.RIBU: 3,
        }

        required = expected[self.move_type]

        if len(self.placements) != required:
            raise ValueError(
                f"{self.move_type.name} requires exactly "
                f"{required} placement(s)."
            )

    def __str__(self):
        placements_str = ", ".join(str(p) for p in self.placements)
        return f"{self.move_type.name}: {placements_str}"
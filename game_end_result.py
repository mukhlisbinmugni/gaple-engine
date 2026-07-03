from dataclasses import dataclass
from enum import Enum, auto

from player import Player


class FinishType(Enum):
    """
    Menjelaskan bagaimana game berakhir.
    """

    NORMAL = auto()
    DOM = auto()
    PASAR = auto()


class SpecialResult(Enum):
    """
    Menjelaskan apakah terjadi kejadian khusus
    setelah game dievaluasi oleh Rule System.
    """

    NONE = auto()

    GUPLAH = auto()
    FAILED_GUPLAH = auto()

    RATUS = auto()
    FAILED_RATUS = auto()

    RIBU = auto()
    FAILED_RIBU = auto()


@dataclass(frozen=True)
class GameEndResult:
    """
    Hasil akhir resmi dari satu game Gaple.

    Game hanya menghasilkan keadaan akhir permainan.
    Rule System kemudian mengisi GameEndResult
    berdasarkan evaluasi rulebook.
    """

    winner: Player
    finish_type: FinishType
    special_result: SpecialResult
    penalty_changes: dict[Player, int]
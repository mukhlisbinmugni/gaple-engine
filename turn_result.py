from dataclasses import dataclass
from enum import Enum, auto

from move import Move
from player import Player


class TurnStatus(Enum):
    PLAY = auto()
    PASS = auto()


@dataclass(frozen=True)
class TurnResult:
    """
    Hasil dari satu giliran permainan.
    """

    player: Player
    move: Move | None
    status: TurnStatus
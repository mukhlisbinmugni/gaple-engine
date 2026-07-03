from player import Player
from game_end_result import (
    FinishType,
    SpecialResult,
    GameEndResult,
)


def test_finish_type():
    assert FinishType.NORMAL.name == "NORMAL"
    assert FinishType.DOM.name == "DOM"
    assert FinishType.PASAR.name == "PASAR"


def test_special_result():
    assert SpecialResult.NONE.name == "NONE"
    assert SpecialResult.GUPLAH.name == "GUPLAH"
    assert SpecialResult.FAILED_GUPLAH.name == "FAILED_GUPLAH"
    assert SpecialResult.RATUS.name == "RATUS"
    assert SpecialResult.FAILED_RATUS.name == "FAILED_RATUS"
    assert SpecialResult.RIBU.name == "RIBU"
    assert SpecialResult.FAILED_RIBU.name == "FAILED_RIBU"


def test_game_end_result_fields():
    winner = Player("Mukhlis")

    penalties = {
        winner: 5
    }

    result = GameEndResult(
        winner=winner,
        finish_type=FinishType.NORMAL,
        special_result=SpecialResult.NONE,
        penalty_changes=penalties
    )

    assert result.winner == winner
    assert result.finish_type == FinishType.NORMAL
    assert result.special_result == SpecialResult.NONE
    assert result.penalty_changes == penalties


def test_penalty_changes():
    p1 = Player("P1")
    p2 = Player("P2")
    p3 = Player("P3")
    p4 = Player("P4")

    penalties = {
        p1: 5,
        p2: -5,
        p3: 0,
        p4: 0
    }

    result = GameEndResult(
        winner=p2,
        finish_type=FinishType.DOM,
        special_result=SpecialResult.NONE,
        penalty_changes=penalties
    )

    assert result.penalty_changes[p1] == 5
    assert result.penalty_changes[p2] == -5
    assert result.penalty_changes[p3] == 0
    assert result.penalty_changes[p4] == 0


def test_winner():
    winner = Player("Mukhlis")

    result = GameEndResult(
        winner=winner,
        finish_type=FinishType.PASAR,
        special_result=SpecialResult.NONE,
        penalty_changes={}
    )

    assert result.winner.name == "Mukhlis"
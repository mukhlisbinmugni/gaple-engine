from deck import Deck


def test_deck_has_28_cards():
    deck = Deck()

    assert len(deck.cards) == 28


def test_all_cards_are_unique():
    deck = Deck()

    assert len(set(deck.cards)) == 28


def test_deal_to_four_players():
    deck = Deck()

    hands = deck.deal()

    assert len(hands) == 4

    for hand in hands:
        assert len(hand) == 7


def test_deal_has_no_duplicate_cards():
    deck = Deck()

    hands = deck.deal()

    all_cards = []

    for hand in hands:
        all_cards.extend(hand)

    assert len(all_cards) == 28
    assert len(set(all_cards)) == 28
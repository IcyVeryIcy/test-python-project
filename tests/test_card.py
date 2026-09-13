"""Tests for card parsing and deck helpers."""

import pytest

from poker_calculator import Card, Rank, Suit, full_deck, parse_cards


def test_card_from_str():
    c = Card.from_str("Ah")
    assert c.rank == Rank.ACE
    assert c.suit == Suit.HEARTS
    assert str(c) == "Ah"


def test_parse_cards_variants():
    assert parse_cards("Ah Kd") == [Card.from_str("Ah"), Card.from_str("Kd")]
    assert parse_cards("Ah,Kd") == parse_cards(["Ah", "Kd"])


def test_invalid_card():
    with pytest.raises(ValueError):
        Card.from_str("XX")
    with pytest.raises(ValueError):
        Card.from_str("A")


def test_full_deck():
    deck = full_deck()
    assert len(deck) == 52
    assert len(set(deck)) == 52


def test_card_ordering():
    assert Card.from_str("2c") < Card.from_str("Ah")
    assert Card.from_str("Kd") < Card.from_str("Ah")

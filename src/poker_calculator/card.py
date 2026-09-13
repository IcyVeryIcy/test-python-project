"""Card, rank, and suit representations for poker."""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from typing import Iterable


class Suit(IntEnum):
    """Playing-card suits."""

    CLUBS = 0
    DIAMONDS = 1
    HEARTS = 2
    SPADES = 3

    def __str__(self) -> str:
        return _SUIT_CHARS[self]

    @classmethod
    def from_char(cls, char: str) -> Suit:
        """Parse a suit from ``c``, ``d``, ``h``, or ``s`` (case-insensitive)."""
        key = char.lower()
        try:
            return _CHAR_TO_SUIT[key]
        except KeyError as exc:
            raise ValueError(f"Invalid suit character: {char!r}") from exc


class Rank(IntEnum):
    """Playing-card ranks from deuce (2) through ace (14)."""

    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13
    ACE = 14

    def __str__(self) -> str:
        return _RANK_CHARS[self]

    @classmethod
    def from_char(cls, char: str) -> Rank:
        """Parse a rank from ``2``–``9``, ``T``, ``J``, ``Q``, ``K``, or ``A``."""
        key = char.upper()
        try:
            return _CHAR_TO_RANK[key]
        except KeyError as exc:
            raise ValueError(f"Invalid rank character: {char!r}") from exc


_SUIT_CHARS = {
    Suit.CLUBS: "c",
    Suit.DIAMONDS: "d",
    Suit.HEARTS: "h",
    Suit.SPADES: "s",
}
_CHAR_TO_SUIT = {v: k for k, v in _SUIT_CHARS.items()}

_RANK_CHARS = {
    Rank.TWO: "2",
    Rank.THREE: "3",
    Rank.FOUR: "4",
    Rank.FIVE: "5",
    Rank.SIX: "6",
    Rank.SEVEN: "7",
    Rank.EIGHT: "8",
    Rank.NINE: "9",
    Rank.TEN: "T",
    Rank.JACK: "J",
    Rank.QUEEN: "Q",
    Rank.KING: "K",
    Rank.ACE: "A",
}
_CHAR_TO_RANK = {v: k for k, v in _RANK_CHARS.items()}


@dataclass(frozen=True, order=True, slots=True)
class Card:
    """A single playing card identified by :class:`Rank` and :class:`Suit`.

    Cards sort by rank then suit. String form is rank+suit, e.g. ``Ah``, ``Td``.
    """

    rank: Rank
    suit: Suit

    def __str__(self) -> str:
        return f"{self.rank}{self.suit}"

    def __repr__(self) -> str:
        return f"Card({self!s})"

    @classmethod
    def from_str(cls, text: str) -> Card:
        """Parse a card from a two-character string like ``Ah`` or ``Td``."""
        text = text.strip()
        if len(text) != 2:
            raise ValueError(f"Card string must be length 2, got {text!r}")
        return cls(Rank.from_char(text[0]), Suit.from_char(text[1]))


def parse_cards(text: str | Iterable[str]) -> list[Card]:
    """Parse one or more cards from a space/comma-separated string or iterable.

    Examples::

        parse_cards("Ah Kd")
        parse_cards("Ah,Kd,Qc")
        parse_cards(["Ah", "Kd"])
    """
    if isinstance(text, str):
        parts = text.replace(",", " ").split()
    else:
        parts = list(text)
    return [Card.from_str(p) for p in parts]


def full_deck() -> list[Card]:
    """Return a standard 52-card deck."""
    return [Card(rank, suit) for rank in Rank for suit in Suit]

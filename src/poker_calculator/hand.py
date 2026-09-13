"""Texas Hold'em hand ranking and evaluation."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from enum import IntEnum
from itertools import combinations
from typing import Sequence

from poker_calculator.card import Card, Rank, parse_cards


class HandCategory(IntEnum):
    """Poker hand categories from weakest to strongest."""

    HIGH_CARD = 0
    ONE_PAIR = 1
    TWO_PAIR = 2
    THREE_OF_A_KIND = 3
    STRAIGHT = 4
    FLUSH = 5
    FULL_HOUSE = 6
    FOUR_OF_A_KIND = 7
    STRAIGHT_FLUSH = 8

    def __str__(self) -> str:
        return _CATEGORY_NAMES[self]


_CATEGORY_NAMES = {
    HandCategory.HIGH_CARD: "High Card",
    HandCategory.ONE_PAIR: "One Pair",
    HandCategory.TWO_PAIR: "Two Pair",
    HandCategory.THREE_OF_A_KIND: "Three of a Kind",
    HandCategory.STRAIGHT: "Straight",
    HandCategory.FLUSH: "Flush",
    HandCategory.FULL_HOUSE: "Full House",
    HandCategory.FOUR_OF_A_KIND: "Four of a Kind",
    HandCategory.STRAIGHT_FLUSH: "Straight Flush",
}


@dataclass(frozen=True, order=True, slots=True)
class HandRank:
    """Comparable strength of a 5-card poker hand.

    Ordering is category first, then kickers (higher is better). Two
    :class:`HandRank` values can be compared with ``<``, ``>``, and ``==``.
    """

    category: HandCategory
    # Tie-break ranks, highest first (e.g. pair rank, then kickers).
    kickers: tuple[int, ...]

    def __str__(self) -> str:
        kicker_str = "-".join(_rank_label(r) for r in self.kickers)
        return f"{self.category} ({kicker_str})"


def _rank_label(value: int) -> str:
    try:
        return str(Rank(value))
    except ValueError:
        return str(value)


def _straight_high(ranks: Sequence[int]) -> int | None:
    """Return the high card of a straight, or None if not a straight.

    Ace can play low for A-2-3-4-5 (wheel); high is then 5.
    """
    uniq = sorted(set(ranks), reverse=True)
    if len(uniq) < 5:
        return None
    # Ace-low wheel
    if set(uniq) >= {14, 5, 4, 3, 2}:
        # Prefer checking contiguous high straights first below; wheel only if needed
        pass
    for i in range(len(uniq) - 4):
        window = uniq[i : i + 5]
        if window[0] - window[4] == 4:
            return window[0]
    # Wheel: A-5-4-3-2
    if {14, 5, 4, 3, 2}.issubset(uniq):
        return 5
    return None


def evaluate_five(cards: Sequence[Card]) -> HandRank:
    """Evaluate exactly five cards and return their :class:`HandRank`."""
    if len(cards) != 5:
        raise ValueError(f"evaluate_five requires exactly 5 cards, got {len(cards)}")
    if len(set(cards)) != 5:
        raise ValueError("Duplicate cards in hand")

    ranks = sorted((c.rank for c in cards), reverse=True)
    suits = [c.suit for c in cards]
    is_flush = len(set(suits)) == 1
    straight_hi = _straight_high(ranks)

    if is_flush and straight_hi is not None:
        return HandRank(HandCategory.STRAIGHT_FLUSH, (straight_hi,))

    counts = Counter(ranks)
    # Groups by frequency desc, then rank desc
    by_count = sorted(counts.items(), key=lambda x: (x[1], x[0]), reverse=True)
    freqs = sorted(counts.values(), reverse=True)

    if freqs[0] == 4:
        quad = by_count[0][0]
        kicker = by_count[1][0]
        return HandRank(HandCategory.FOUR_OF_A_KIND, (quad, kicker))

    if freqs[0] == 3 and freqs[1] == 2:
        trip = by_count[0][0]
        pair = by_count[1][0]
        return HandRank(HandCategory.FULL_HOUSE, (trip, pair))

    if is_flush:
        return HandRank(HandCategory.FLUSH, tuple(ranks))

    if straight_hi is not None:
        return HandRank(HandCategory.STRAIGHT, (straight_hi,))

    if freqs[0] == 3:
        trip = by_count[0][0]
        kickers = tuple(r for r, _ in by_count[1:])
        return HandRank(HandCategory.THREE_OF_A_KIND, (trip, *kickers))

    if freqs[0] == 2 and freqs[1] == 2:
        high_pair = by_count[0][0]
        low_pair = by_count[1][0]
        kicker = by_count[2][0]
        return HandRank(HandCategory.TWO_PAIR, (high_pair, low_pair, kicker))

    if freqs[0] == 2:
        pair = by_count[0][0]
        kickers = tuple(r for r, _ in by_count[1:])
        return HandRank(HandCategory.ONE_PAIR, (pair, *kickers))

    return HandRank(HandCategory.HIGH_CARD, tuple(ranks))


def evaluate(cards: Sequence[Card] | str) -> HandRank:
    """Evaluate the best 5-card poker hand from 5–7 cards.

    Accepts a sequence of :class:`Card` or a parseable string such as
    ``"Ah Kd Qc Jh Ts"``.
    """
    if isinstance(cards, str):
        cards = parse_cards(cards)
    cards = list(cards)
    n = len(cards)
    if n < 5 or n > 7:
        raise ValueError(f"evaluate requires 5–7 cards, got {n}")
    if len(set(cards)) != n:
        raise ValueError("Duplicate cards in hand")
    if n == 5:
        return evaluate_five(cards)
    return max(evaluate_five(combo) for combo in combinations(cards, 5))


def hand_name(cards: Sequence[Card] | str) -> str:
    """Return a human-readable name for the best hand (e.g. ``\"Flush\"``)."""
    return str(evaluate(cards).category)


def compare_hands(
    hand_a: Sequence[Card] | str,
    hand_b: Sequence[Card] | str,
) -> int:
    """Compare two hands: ``1`` if A wins, ``-1`` if B wins, ``0`` on tie."""
    rank_a = evaluate(hand_a)
    rank_b = evaluate(hand_b)
    if rank_a > rank_b:
        return 1
    if rank_a < rank_b:
        return -1
    return 0

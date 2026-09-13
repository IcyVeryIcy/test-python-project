"""poker-calculator: Texas Hold'em hand evaluation and equity calculation.

Quickstart
----------
>>> from poker_calculator import Card, evaluate, calculate_equity, parse_cards
>>> evaluate("Ah Kh Qh Jh Th")  # royal flush
HandRank(...)
>>> calculate_equity(["As Ad", "Kh Kd"], board="2c 7d 9h", iterations=5000)
EquityResult(...)

Public API
----------
* :class:`Card`, :class:`Rank`, :class:`Suit`, :func:`parse_cards`, :func:`full_deck`
* :class:`HandCategory`, :class:`HandRank`, :func:`evaluate`, :func:`evaluate_five`
* :func:`hand_name`, :func:`compare_hands`
* :class:`EquityResult`, :func:`calculate_equity`, :func:`heads_up_equity`
"""

from poker_calculator.card import Card, Rank, Suit, full_deck, parse_cards
from poker_calculator.equity import EquityResult, calculate_equity, heads_up_equity
from poker_calculator.hand import (
    HandCategory,
    HandRank,
    compare_hands,
    evaluate,
    evaluate_five,
    hand_name,
)

__version__ = "0.1.0"

__all__ = [
    "Card",
    "Rank",
    "Suit",
    "parse_cards",
    "full_deck",
    "HandCategory",
    "HandRank",
    "evaluate",
    "evaluate_five",
    "hand_name",
    "compare_hands",
    "EquityResult",
    "calculate_equity",
    "heads_up_equity",
    "__version__",
]

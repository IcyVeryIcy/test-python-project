"""Equity and odds helpers for Texas Hold'em."""

from __future__ import annotations

import itertools
import random
from dataclasses import dataclass
from typing import Sequence

from poker_calculator.card import Card, full_deck, parse_cards
from poker_calculator.hand import evaluate


@dataclass(frozen=True, slots=True)
class EquityResult:
    """Win / tie / loss shares for each player.

    ``equity`` is the fair share of the pot: wins + ties / n_tied.
    Values are fractions in ``[0, 1]`` and sum to approximately 1.0.
    """

    wins: tuple[float, ...]
    ties: tuple[float, ...]
    equity: tuple[float, ...]
    iterations: int
    exact: bool

    def as_percentages(self) -> tuple[float, ...]:
        """Return equity values as percentages (0–100)."""
        return tuple(e * 100.0 for e in self.equity)


def _normalize_hole(hole: Sequence[Card] | str) -> list[Card]:
    cards = parse_cards(hole) if isinstance(hole, str) else list(hole)
    if len(cards) != 2:
        raise ValueError(f"Each hole hand must have exactly 2 cards, got {len(cards)}")
    return cards


def _normalize_board(board: Sequence[Card] | str | None) -> list[Card]:
    if board is None:
        return []
    cards = parse_cards(board) if isinstance(board, str) else list(board)
    if len(cards) > 5:
        raise ValueError(f"Board may have at most 5 cards, got {len(cards)}")
    return cards


def _remaining_deck(used: Sequence[Card]) -> list[Card]:
    used_set = set(used)
    if len(used_set) != len(used):
        raise ValueError("Duplicate cards among hole cards / board")
    return [c for c in full_deck() if c not in used_set]




def calculate_equity(
    hole_hands: Sequence[Sequence[Card] | str],
    board: Sequence[Card] | str | None = None,
    *,
    iterations: int = 10_000,
    seed: int | None = None,
    exact_threshold: int = 50_000,
) -> EquityResult:
    """Estimate or exactly compute equity for two or more Hold'em hands.

    Parameters
    ----------
    hole_hands:
        Two or more 2-card hole hands (``Card`` sequences or strings like
        ``\"Ah Kd\"``).
    board:
        0–5 community cards already dealt.
    iterations:
        Monte Carlo sample count when exact enumeration is impractical.
    seed:
        Optional RNG seed for reproducible Monte Carlo runs.
    exact_threshold:
        If the number of ways to complete the board is at most this value,
        use exact enumeration instead of Monte Carlo.

    Returns
    -------
    EquityResult
        Per-player win rates, tie rates, and pot equity.
    """
    if len(hole_hands) < 2:
        raise ValueError("Need at least two hole hands")

    holes = [_normalize_hole(h) for h in hole_hands]
    board_cards = _normalize_board(board)
    used = [c for h in holes for c in h] + board_cards
    remaining = _remaining_deck(used)
    need = 5 - len(board_cards)
    n_players = len(holes)

    if need == 0:
        win_counts = [0.0] * n_players
        tie_counts = [0.0] * n_players
        # Recompute with proper tie accounting
        ranks = [evaluate(list(h) + board_cards) for h in holes]
        best = max(ranks)
        winners = [i for i, r in enumerate(ranks) if r == best]
        if len(winners) == 1:
            win_counts[winners[0]] = 1.0
        else:
            share = 1.0 / len(winners)
            for i in winners:
                tie_counts[i] = 1.0
                win_counts[i] = share
        equity = tuple(win_counts)
        ties = tuple(tie_counts)
        # wins as exclusive wins (not pot share)
        exclusive_wins = tuple(
            1.0 if (i in winners and len(winners) == 1) else 0.0 for i in range(n_players)
        )
        return EquityResult(
            wins=exclusive_wins,
            ties=ties,
            equity=equity,
            iterations=1,
            exact=True,
        )

    total_combos = 1
    n = len(remaining)
    for i in range(need):
        total_combos *= n - i
    for i in range(1, need + 1):
        total_combos //= i

    use_exact = total_combos <= exact_threshold

    exclusive_wins = [0.0] * n_players
    tie_counts = [0.0] * n_players
    equity_sum = [0.0] * n_players

    def record(board_extra: Sequence[Card]) -> None:
        full_board = board_cards + list(board_extra)
        ranks = [evaluate(list(h) + full_board) for h in holes]
        best = max(ranks)
        winners = [i for i, r in enumerate(ranks) if r == best]
        if len(winners) == 1:
            exclusive_wins[winners[0]] += 1.0
            equity_sum[winners[0]] += 1.0
        else:
            share = 1.0 / len(winners)
            for i in winners:
                tie_counts[i] += 1.0
                equity_sum[i] += share

    if use_exact:
        for combo in itertools.combinations(remaining, need):
            record(combo)
        total = float(total_combos)
        return EquityResult(
            wins=tuple(w / total for w in exclusive_wins),
            ties=tuple(t / total for t in tie_counts),
            equity=tuple(e / total for e in equity_sum),
            iterations=total_combos,
            exact=True,
        )

    rng = random.Random(seed)
    for _ in range(iterations):
        sample = rng.sample(remaining, need)
        record(sample)
    total = float(iterations)
    return EquityResult(
        wins=tuple(w / total for w in exclusive_wins),
        ties=tuple(t / total for t in tie_counts),
        equity=tuple(e / total for e in equity_sum),
        iterations=iterations,
        exact=False,
    )


def heads_up_equity(
    hand_a: Sequence[Card] | str,
    hand_b: Sequence[Card] | str,
    board: Sequence[Card] | str | None = None,
    **kwargs: object,
) -> EquityResult:
    """Convenience wrapper for two-player equity."""
    return calculate_equity([hand_a, hand_b], board=board, **kwargs)  # type: ignore[arg-type]

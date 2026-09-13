# poker-calculator

Texas Hold'em hand evaluation and equity/odds calculation for Python 3.10+.

Pure standard library at runtime — no NumPy required.

## Install

```bash
pip install -e ".[dev]"
```

Or from the project directory without extras:

```bash
pip install -e .
```

## Quickstart

```python
from poker_calculator import evaluate, hand_name, calculate_equity, parse_cards

# Evaluate 5–7 cards (best five-card hand)
rank = evaluate("Ah Kh Qh Jh Th")
print(rank.category)   # HandCategory.STRAIGHT_FLUSH
print(hand_name("Kc Kd Kh 2s 2d"))  # Full House

# Compare / inspect
from poker_calculator import compare_hands, HandCategory
assert compare_hands("Ah Kd Qc Jh Ts", "9c 9d 9h 2s 2d") == 1

# Equity: Monte Carlo (or exact when the board completion space is small)
result = calculate_equity(
    ["As Ad", "Kh Kd"],
    board="2c 7d 9h",
    iterations=10_000,
    seed=42,
)
print(result.equity)           # e.g. (0.93..., 0.06...)
print(result.as_percentages()) # percent form
print(result.exact)            # True if fully enumerated
```

Cards can be `Card` objects or short strings (`Ah`, `Td`, `2c`). Hole hands and boards accept space- or comma-separated strings.

## API overview

| Symbol | Description |
|--------|-------------|
| `Card`, `Rank`, `Suit` | Immutable card representation |
| `parse_cards`, `full_deck` | Parsing helpers and a 52-card deck |
| `HandCategory`, `HandRank` | Hand category enum and comparable strength |
| `evaluate` / `evaluate_five` | Best-hand evaluation for 5–7 / exactly 5 cards |
| `hand_name`, `compare_hands` | Convenience wrappers |
| `EquityResult` | `wins`, `ties`, `equity`, `iterations`, `exact` |
| `calculate_equity` | Multiway equity (exact or Monte Carlo) |
| `heads_up_equity` | Two-player convenience wrapper |

### Equity behaviour

- **River (5 board cards):** single deterministic comparison.
- **Turn / small spaces:** exact enumeration when the number of board completions ≤ `exact_threshold` (default 50 000).
- **Flop / preflop:** Monte Carlo sampling (`iterations`, optional `seed`).

## Development

```bash
pip install -e ".[dev]"
pytest
ruff check src tests
```

## License

MIT

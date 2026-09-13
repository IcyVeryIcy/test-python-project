"""Tests for equity / odds helpers."""

import pytest

from poker_calculator import calculate_equity, heads_up_equity


def test_pocket_aces_vs_kings_preflop():
    result = calculate_equity(
        ["As Ad", "Kh Kd"],
        iterations=3000,
        seed=42,
        exact_threshold=0,  # force Monte Carlo
    )
    assert not result.exact
    assert result.equity[0] > result.equity[1]
    assert result.equity[0] > 0.75  # AA vs KK ~81%
    assert abs(sum(result.equity) - 1.0) < 1e-9


def test_exact_on_river():
    # Both hands known; board complete — deterministic
    result = calculate_equity(
        ["As Kd", "Qh Qc"],
        board="Ah 7c 3d 2s 9h",
    )
    assert result.exact
    assert result.iterations == 1
    assert result.equity[0] == 1.0
    assert result.equity[1] == 0.0


def test_exact_tie_on_river():
    result = calculate_equity(
        ["As Kd", "Ad Kh"],
        board="Ac 7c 3d 2s 9h",
    )
    assert result.exact
    assert result.equity[0] == pytest.approx(0.5)
    assert result.equity[1] == pytest.approx(0.5)
    assert result.ties[0] == 1.0


def test_exact_turn_enumeration():
    # One card to come — C(45,1)=45 or fewer remaining; exact by default
    result = calculate_equity(
        ["As Ad", "Kh Kd"],
        board="2c 7d 9h 3s",
    )
    assert result.exact
    assert sum(result.equity) == pytest.approx(1.0)
    assert result.equity[0] > result.equity[1]


def test_heads_up_wrapper():
    result = heads_up_equity("As Ad", "7h 2c", board="Ah Kd 9c", iterations=2000, seed=1)
    assert len(result.equity) == 2
    assert result.equity[0] > 0.9


def test_as_percentages():
    result = calculate_equity(["As Ad", "Kh Kd"], board="Ah 7c 3d 2s 9h")
    pct = result.as_percentages()
    assert pct[0] == pytest.approx(100.0)


def test_invalid_inputs():
    with pytest.raises(ValueError):
        calculate_equity(["As Ad"])
    with pytest.raises(ValueError):
        calculate_equity(["As Ad Kd", "Kh Kd"])
    with pytest.raises(ValueError):
        calculate_equity(["As Ad", "As Kh"])  # duplicate ace of spades

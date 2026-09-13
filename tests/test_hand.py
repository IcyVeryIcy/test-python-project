"""Tests for Texas Hold'em hand evaluation."""

import pytest

from poker_calculator import (
    HandCategory,
    compare_hands,
    evaluate,
    evaluate_five,
    hand_name,
    parse_cards,
)


def test_royal_flush():
    rank = evaluate("Ah Kh Qh Jh Th")
    assert rank.category == HandCategory.STRAIGHT_FLUSH
    assert rank.kickers[0] == 14


def test_straight_flush_wheel():
    rank = evaluate("Ah 2h 3h 4h 5h")
    assert rank.category == HandCategory.STRAIGHT_FLUSH
    assert rank.kickers[0] == 5


def test_four_of_a_kind():
    rank = evaluate("9c 9d 9h 9s 2c")
    assert rank.category == HandCategory.FOUR_OF_A_KIND
    assert rank.kickers[0] == 9


def test_full_house():
    rank = evaluate("Kc Kd Kh 2s 2d")
    assert rank.category == HandCategory.FULL_HOUSE
    assert rank.kickers == (13, 2)


def test_flush():
    rank = evaluate("Ah Kh 9h 4h 2h")
    assert rank.category == HandCategory.FLUSH


def test_straight():
    rank = evaluate("9c 8d 7h 6s 5c")
    assert rank.category == HandCategory.STRAIGHT
    assert rank.kickers[0] == 9


def test_wheel_straight():
    rank = evaluate("Ac 2d 3h 4s 5c")
    assert rank.category == HandCategory.STRAIGHT
    assert rank.kickers[0] == 5


def test_three_of_a_kind():
    rank = evaluate("7c 7d 7h As Kd")
    assert rank.category == HandCategory.THREE_OF_A_KIND


def test_two_pair():
    rank = evaluate("Jc Jd 4h 4s 9c")
    assert rank.category == HandCategory.TWO_PAIR
    assert rank.kickers[:2] == (11, 4)


def test_one_pair():
    rank = evaluate("Ac Ad 8h 5s 2c")
    assert rank.category == HandCategory.ONE_PAIR
    assert rank.kickers[0] == 14


def test_high_card():
    rank = evaluate("Ac Kd 9h 5s 2c")
    assert rank.category == HandCategory.HIGH_CARD


def test_best_of_seven():
    # Board + hole yields flush
    rank = evaluate("Ah Kh 2c 7d 9h 4h 3h")
    assert rank.category == HandCategory.FLUSH


def test_best_of_six():
    rank = evaluate("As Ad Ac Ah 2c 3d")
    assert rank.category == HandCategory.FOUR_OF_A_KIND


def test_compare_hands():
    assert compare_hands("Ah Kh Qh Jh Th", "9c 9d 9h 9s 2c") == 1
    assert compare_hands("Ac Ad 8h 5s 2c", "Ah Kh Qh Jh Th") == -1
    assert compare_hands("Ac Ad 8h 5s 2c", "As Ah 8d 5c 2d") == 0


def test_hand_name():
    assert hand_name("Kc Kd Kh 2s 2d") == "Full House"


def test_duplicate_cards_rejected():
    with pytest.raises(ValueError):
        evaluate("Ah Ah Kd Qc Js")


def test_wrong_count_rejected():
    with pytest.raises(ValueError):
        evaluate("Ah Kd")
    with pytest.raises(ValueError):
        evaluate_five(parse_cards("Ah Kd Qc Js"))


def test_kicker_ordering():
    # Higher kicker wins
    assert evaluate("Ac Ad Kh 9s 2c") > evaluate("As Ah Qd 9c 2d")

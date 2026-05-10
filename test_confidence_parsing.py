import math

from app import extract_confidence


def test_extract_confidence_standard_percent():
    assert extract_confidence("Confidence Score: 87%") == 87.0


def test_extract_confidence_confidence_keyword():
    assert extract_confidence("Confidence: 92 %") == 92.0


def test_extract_confidence_dash_separator():
    assert extract_confidence("Confidence Score - 77%") == 77.0


def test_extract_confidence_decimal_percent():
    # should parse numeric value and return as float
    assert extract_confidence("Confidence Score: 88.5%") == 88.5


def test_extract_confidence_decimal_0_to_1():
    # Treat 0-1 as percent
    assert extract_confidence("Confidence Score: 0.87") == 87.0


def test_extract_confidence_out_of_range_returns_none():
    assert extract_confidence("Confidence Score: 120%") is None


def test_extract_confidence_no_confidence_none():
    assert extract_confidence("Some other text without confidence") is None


def test_extract_confidence_confidence_keyword_percent_in_parentheses():
    assert extract_confidence("(Confidence: 87%)") == 87.0


def test_extract_confidence_confidence_equals_percent():
    assert extract_confidence("Confidence=88.5%") == 88.5


def test_extract_confidence_confidence_is_probability():
    assert extract_confidence("Confidence score is 0.91") == 91.0


def test_extract_confidence_confidence_word_without_percent_assumes_percent():
    assert extract_confidence("Confidence: 87") == 87.0


def test_extract_confidence_dash_em_dash_variant():
    assert extract_confidence("Confidence Score — 77%") == 77.0


def test_extract_confidence_approx_prefix():
    assert extract_confidence("Confidence: ~87%") == 87.0


def test_extract_confidence_word_percent():
    assert extract_confidence("Confidence: 87 percent") == 87.0


def test_extract_confidence_decimal_0_1_with_parens():
    assert extract_confidence("Confidence: 0.87 (87%)") == 87.0


def test_extract_confidence_confidence_over_100_out_of_fraction():
    # "87 / 100" -> 87% (special-cased)
    assert extract_confidence("Confidence: 87 / 100") == 87.0


def test_extract_confidence_inline_trailing_text():
    assert extract_confidence("Confidence Score: 88.5% (moderate)") == 88.5


def test_extract_confidence_confident_suffix():
    assert extract_confidence("The model is 87% confident in this diagnosis.") == 87.0


def test_extract_confidence_approximate_prefix():
    assert extract_confidence("Confidence score is approximately 87%.") == 87.0


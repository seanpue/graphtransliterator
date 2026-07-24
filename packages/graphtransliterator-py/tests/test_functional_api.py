import pytest

from graphtransliterator import (
    GraphTransliterator,
    match_at,
    tokenize,
    transliterate,
    transliterate_with_details,
)


@pytest.fixture
def sample_gt():
    """Provides a simple GraphTransliterator instance for functional testing."""
    yaml_config = """
    tokens:
      a: [vowel]
      aa: [vowel]
      b: [consonant]
      ' ': [wb]
    rules:
      a: A
      aa: <DOUBLE_A>
      b: B
      ' ': ' '
    whitespace:
      default: " "
      consolidate: false
      token_class: wb
    """
    return GraphTransliterator.from_yaml(yaml_config)


def test_functional_tokenize(sample_gt):
    """Test module-level tokenize function."""
    tokens = tokenize(sample_gt, "aba")
    # Verify default whitespace token padding occurs
    assert tokens == [" ", "a", "b", "a", " "]


def test_functional_transliterate(sample_gt):
    """Test module-level transliterate function."""
    output = transliterate(sample_gt, "a ab")
    assert output == "A AB"


def test_functional_transliterate_with_details(sample_gt):
    """Test module-level transliterate_with_details function."""
    output, rules = transliterate_with_details(sample_gt, "aa")
    assert output == "<DOUBLE_A>"
    assert len(rules) == 1  # Start whitespace, 'aa', end whitespace
    assert rules[0].get("production") == "<DOUBLE_A>"


def test_functional_match_at(sample_gt):
    """Test module-level match_at function."""
    tokens = tokenize(sample_gt, "aa")

    # Single match mode (returns best match index)
    best_match = match_at(sample_gt, 1, tokens, match_all=False)
    assert isinstance(best_match, int)
    assert sample_gt.rules[best_match].get("production") == "<DOUBLE_A>"

    # Match all mode (returns list of matching rule indexes)
    all_matches = match_at(sample_gt, 1, tokens, match_all=True)
    assert isinstance(all_matches, list)
    assert len(all_matches) > 0


def test_functional_api_exports():
    """Verify that the module-level helper functions are exported at top level."""
    import graphtransliterator as gt

    assert hasattr(gt, "tokenize")
    assert hasattr(gt, "transliterate")
    assert hasattr(gt, "transliterate_with_details")
    assert hasattr(gt, "match_at")

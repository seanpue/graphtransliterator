import pytest
from graphtransliterator import (
    GraphTransliterator,
    WhitespaceRule,
)
from graphtransliterator.initialize import _transliteration_rule_of


@pytest.fixture
def default_whitespace():
    return WhitespaceRule(default=" ", token_class="space", consolidate=True)


@pytest.fixture
def base_transliterator(default_whitespace):
    """Base transliterator that handles basic Latin alphabet mapping."""
    tokens = {
        "a": ["latin"],
        "b": ["latin"],
        " ": ["space"],
    }
    rules = [
        _transliteration_rule_of({"tokens": ["a"], "production": "A"}),
        _transliteration_rule_of({"tokens": ["b"], "production": "B"}),
        _transliteration_rule_of({"tokens": [" "], "production": " "}),
    ]
    return GraphTransliterator(
        tokens=tokens,
        rules=rules,
        whitespace=default_whitespace,
        metadata={"name": "Base Engine"},
    )


@pytest.fixture
def greek_subgraph(default_whitespace):
    """Secondary transliterator handling Greek characters."""
    tokens = {
        "a_g": ["greek"],
        "b_g": ["greek"],
        " ": ["space"],
    }
    # Exclude duplicate space rule here to prevent rule ambiguity on injection
    rules = [
        _transliteration_rule_of({"tokens": ["a_g"], "production": "α"}),
        _transliteration_rule_of({"tokens": ["b_g"], "production": "β"}),
    ]
    return GraphTransliterator(
        tokens=tokens,
        rules=rules,
        whitespace=default_whitespace,
        metadata={"version": "subgraph_v1"},
    )


def test_basic_subgraph_injection(base_transliterator, greek_subgraph):
    """Tests injecting a subgraph without prefix constraints."""
    injected_gt = base_transliterator.inject_subgraph(greek_subgraph)

    # Transliterates base and injected rules cleanly across spaces
    assert injected_gt.transliterate("a b a_g b_g") == "A B α β"

    # Verify merged token classes
    assert "latin" in injected_gt.tokens["a"]
    assert "greek" in injected_gt.tokens["a_g"]


def test_subgraph_injection_with_prefix_tokens(base_transliterator, greek_subgraph):
    """Tests injecting a subgraph where rules are scoped under prefix tokens."""
    # Add a math mode flag token to the base configuration
    base_tokens = dict(base_transliterator.tokens)
    base_tokens["$"] = ["math_marker"]

    base_gt = GraphTransliterator(
        tokens=base_tokens,
        rules=base_transliterator.rules + [_transliteration_rule_of({"tokens": ["$"], "production": "$"})],
        whitespace=base_transliterator.whitespace,
    )

    # Inject the Greek subgraph scoped strictly behind the '$' token
    scoped_gt = base_gt.inject_subgraph(greek_subgraph, prefix_tokens=["$"])

    # Greek tokens without the prefix should fail to match
    with pytest.raises(Exception):
        scoped_gt.transliterate("a_g")

    # Each injected Greek token must immediately follow a '$' to satisfy the lookbehind rule
    assert scoped_gt.transliterate("$a_g $b_g") == "$α $β"


def test_subgraph_whitespace_mismatch_raises_error(base_transliterator):
    """Tests that injecting a subgraph with mismatched whitespace rules raises a ValueError."""
    mismatched_ws = WhitespaceRule(default=" ", token_class="space", consolidate=False)
    incompatible_subgraph = GraphTransliterator(
        tokens={"x": ["letter"]},
        rules=[_transliteration_rule_of({"tokens": ["x"], "production": "X"})],
        whitespace=mismatched_ws,
    )

    with pytest.raises(ValueError, match="Configuration Mismatch"):
        base_transliterator.inject_subgraph(incompatible_subgraph)


def test_subgraph_injection_with_multiple_prefix_tokens(base_transliterator, greek_subgraph):
    """Tests injecting a subgraph requiring a multi-token lookbehind sequence."""
    base_tokens = dict(base_transliterator.tokens)
    base_tokens["\\"] = ["escape"]
    base_tokens["g"] = ["mode_switch"]

    base_gt = GraphTransliterator(
        tokens=base_tokens,
        rules=base_transliterator.rules
        + [
            _transliteration_rule_of({"tokens": ["\\"], "production": "\\"}),
            _transliteration_rule_of({"tokens": ["g"], "production": "g"}),
        ],
        whitespace=base_transliterator.whitespace,
    )

    # Requires the exact sequential prefix of \ followed by g
    scoped_gt = base_gt.inject_subgraph(greek_subgraph, prefix_tokens=["\\", "g"])

    # Partial prefix or missing escape sequence should fail lookbehind
    with pytest.raises(Exception):
        scoped_gt.transliterate("g a_g")

    # The target tokens must directly abut the \g prefix sequence
    assert scoped_gt.transliterate("\\ga_g \\gb_g") == "\\gα \\gβ"


def test_subgraph_injection_preserves_base_lookahead(base_transliterator, greek_subgraph):
    """Ensure lookahead rules on the base engine remain intact after injection."""
    # Add a base rule with a lookahead constraint
    base_tokens = dict(base_transliterator.tokens)
    base_tokens["!"] = ["exclamation"]

    rule_with_lookahead = _transliteration_rule_of(
        {"tokens": ["a"], "next_tokens": ["!"], "production": "A_EXCLAMATION"}
    )

    base_gt = GraphTransliterator(
        tokens=base_tokens,
        rules=base_transliterator.rules
        + [rule_with_lookahead, _transliteration_rule_of({"tokens": ["!"], "production": "!"})],
        whitespace=base_transliterator.whitespace,
    )

    injected_gt = base_gt.inject_subgraph(greek_subgraph)

    # 'a' followed by '!' should trigger the lookahead rule
    assert injected_gt.transliterate("a!") == "A_EXCLAMATION!"


def test_rshift_operator_subgraph_injection():
    """Verify that the '>>' operator overloads inject_subgraph correctly."""
    base_yaml = """
    tokens:
        a: [vowel]
        ' ': [wb]
    rules:
        a: A
    whitespace:
        default: ' '
        consolidate: true
        token_class: wb
    """
    sub1_yaml = """
    tokens:
        b: [consonant]
        ' ': [wb]
    rules:
        b: B
    whitespace:
        default: ' '
        consolidate: true
        token_class: wb
    """
    sub2_yaml = """
    tokens:
        c: [consonant]
        ' ': [wb]
    rules:
        c: C
    whitespace:
        default: ' '
        consolidate: true
        token_class: wb
    """

    gt_base = GraphTransliterator.from_yaml(base_yaml)
    gt_sub1 = GraphTransliterator.from_yaml(sub1_yaml)
    gt_sub2 = GraphTransliterator.from_yaml(sub2_yaml)

    # 1. Assert >> operator behaves identically to inject_subgraph()
    gt_rshift = gt_base >> gt_sub1
    gt_method = gt_base.inject_subgraph(gt_sub1)

    assert gt_rshift.transliterate("ab") == "AB"
    assert gt_rshift.transliterate("ab") == gt_method.transliterate("ab")

    # 2. Test chaining using the operator (gt_base >> gt_sub1 >> gt_sub2)
    gt_chained = gt_base >> gt_sub1 >> gt_sub2
    assert gt_chained.transliterate("abc") == "ABC"

    # 3. Assert TypeError when using >> with a non-GraphTransliterator object
    with pytest.raises(TypeError):
        _ = gt_base >> "invalid_type"

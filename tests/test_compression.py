# -*- coding: utf-8 -*-

"""Tests for compression/decompression."""
import graphtransliterator
import graphtransliterator.compression as compression
from graphtransliterator import GraphTransliterator
import json
import pytest


test_config = """
tokens:
  a: [class_a]
  b: [class_b]
  c: [class_c]
  " ": [wb]
  d: []
  Aa: [contrained_rule]
rules:
  a: A
  b: B
  <class_c> <class_c> a: A(AFTER_CLASS_C_AND_CLASS_C)
  (<class_c> b) a: A(AFTER_B_AND_CLASS_C)
  (<class_c> b b) a a: AA(AFTER_BB_AND_CLASS_C)
  a <class_c>: A(BEFORE_CLASS_C)
  a b (c <class_b>): AB(BEFORE_C_AND_CLASS_B)
  c: C
  c c: C*2
  a (b b b): A(BEFORE_B_B_B)
  d (c <class_a>): D(BEFORE_C_AND_CLASS_A)
  (b b) a: A(AFTER_B_B)
  <wb> Aa: A(ONLY_A_CONSTRAINED_RULE)
  d d: "<DD>"
  d: "<D>"
  " ": " "
onmatch_rules:
  -
      <class_a> <class_b> + <class_a> <class_b>: "!"
  -
      <class_a> + <class_b>: ","
whitespace:
  default: ' '
  consolidate: True
  token_class: wb
"""


def test_compression():
    gt = GraphTransliterator.from_yaml(test_config)
    compressed_config = compression.compress_config(gt.dump())
    decompressed_config = compression.decompress_config(compressed_config)
    gt_from_decompressed = GraphTransliterator.load(decompressed_config)
    # Compare JSON dumps with sorted keys.
    assert (
        json.dumps(gt.dump(), sort_keys=True) ==
        json.dumps(gt_from_decompressed.dump(), sort_keys=True)
    )
    # Test bad compression level
    with pytest.raises(ValueError):
        gt.dump(compression_level=graphtransliterator.HIGHEST_COMPRESSION_LEVEL+1)
    # Test compression at level 0 (should likely not be called)
    assert "compressed_settings" not in compression.compress_config(
        gt.dump(), compression_level=0
    )
    # Test compression levels
    assert '"tokens": ' in gt.dumps(compression_level=0)
    assert '"compressed_settings"' in gt.dumps(compression_level=1)
    assert '"compressed_settings"' in gt.dumps(compression_level=2)
    for i in range(0, graphtransliterator.HIGHEST_COMPRESSION_LEVEL+1):
        x = gt.dumps(compression_level=i)
        y = gt.loads(x)
        assert y.transliterate("a") == "A"

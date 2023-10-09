#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `graphtransliterator` package."""

from click.testing import CliRunner
from graphtransliterator import cli
from graphtransliterator import GraphTransliterator
from graphtransliterator import __version__ as version
from graphtransliterator.transliterators import Example
from io import StringIO
import json
import os
import yaml


def test_command_line_interface():
    """Test the CLI."""
    runner = CliRunner()
    result = runner.invoke(cli.main)
    assert result.exit_code == 0
    assert "main" in result.output
    help_result = runner.invoke(cli.main, ["--help"])
    assert help_result.exit_code == 0
    assert "Show this message and exit." in help_result.output


def test_command_line_version():
    """Test CLI version."""
    runner = CliRunner()
    version_result = runner.invoke(cli.main, ["--version"])
    assert f"{version}" in version_result.output


test_yaml = """
    tokens:
      a: [vowel]
      ' ': [whitespace]
    rules:
      a: A
      ' ': ' '
    onmatch_rules:
      - <vowel> + <vowel>: ","
    whitespace:
      consolidate: False
      default: " "
      token_class: whitespace
"""


def test_cli_transliterate_tests(tmpdir):
    """Tests transliterate command, and loading of all formats."""
    transliterator = GraphTransliterator.from_yaml(test_yaml)

    runner = CliRunner()

    # test bundled
    bundled_result = runner.invoke(
        cli.main, ["transliterate", "--from", "bundled", "Example", "a"]
    )
    assert bundled_result.exit_code == 0
    assert bundled_result.output.strip() == "A"

    # test multiple inputs with python output
    bundled_multiple_result = runner.invoke(
        cli.main, ["transliterate", "--from", "bundled", "Example", "a", "a"]
    )
    assert bundled_multiple_result.exit_code == 0
    assert bundled_multiple_result.output.strip() == str(["A", "A"])

    # test json
    bundled_multiple_json_result = runner.invoke(
        cli.main,
        ["transliterate", "--from", "bundled", "Example", "--to", "json", "a", "a"],
    )
    assert bundled_multiple_json_result.exit_code == 0
    assert bundled_multiple_json_result.output.strip() == json.dumps(["A", "A"])

    # test transliterate from JSON
    json_ = transliterator.dumps()
    json_result = runner.invoke(
        cli.main, ["transliterate", "--from", "json", json_, "a"]
    )
    assert json_result.exit_code == 0
    assert json_result.output.strip() == "A"

    # test transliterate from json file
    json_file = tmpdir.mkdir("sub").join("test.json")
    json_file.write(json_)
    json_file_result = runner.invoke(
        cli.main, ["transliterate", "--from", "json_file", json_file.strpath, "a"]
    )
    assert json_file_result.exit_code == 0
    assert json_file_result.output.strip() == "A"

    # test transliterate from yaml file
    yaml_file = tmpdir.join("test.yaml")
    yaml_file.write(test_yaml)
    yaml_file_result = runner.invoke(
        cli.main, ["transliterate", "--from", "yaml_file", yaml_file.strpath, "a"]
    )
    assert yaml_file_result.exit_code == 0
    assert yaml_file_result.output.strip() == "A"


def test_cli_generate_tests():
    """Test tests command."""
    runner = CliRunner()
    gen_tests_result = runner.invoke(
        cli.main, ["generate-tests", "--from", "bundled", "Example"]
    )
    assert gen_tests_result.exit_code == 0
    yaml_ = yaml.safe_load(StringIO(gen_tests_result.output))
    assert len(yaml_) == 5 and type(yaml_) == dict


def test_cli_dump():
    """Test `dump` command."""
    runner = CliRunner()
    dump_result = runner.invoke(cli.main, ["dump", "--from", "bundled", "Example"])
    assert dump_result.exit_code == 0
    json_ = dump_result.output
    assert GraphTransliterator.loads(json_).transliterate("a") == "A"
    # check that dump remains the same (important for version control)
    for i in range(0, 50):
        _ = runner.invoke(cli.main, ["dump", "--from", "bundled", "Example"])
        assert _.output == json_, "JSON dump varies"


def test_cli_test():
    """Test `test` command."""
    runner = CliRunner()
    test_result = runner.invoke(cli.main, ["test", "Example"])
    assert test_result.exit_code == 0
    assert test_result.output.strip() == "True"


def test_make_json():
    """Tests `make-json` command."""
    runner = CliRunner()
    # Because make-json generates a JSON file, which may differ slightly from original,
    # save and later restore original JSON file.
    orig_filename = os.path.join(Example().directory, "example.json")
    with open(orig_filename, "r") as f:
        orig_json = f.read()
    test_result = runner.invoke(cli.main, ["make-json", "Example"])
    assert test_result.exit_code == 0
    # Test regex matching
    test_result = runner.invoke(cli.main, ["make-json", "-re", "Examp"])
    assert "Made JSON of" in test_result.output
    assert test_result.exit_code == 0
    # Test regex not Matching
    test_result = runner.invoke(cli.main, ["make-json", "-re", "!"])
    assert "No bundled transliterator found " in test_result.output
    assert test_result.exit_code == 0  # no error here
    # Restore JSON file
    with open(orig_filename, "w") as f:
        f.write(orig_json)


def test_list_bundled():
    runner = CliRunner()
    test_result = runner.invoke(cli.main, ["list-bundled"])
    assert "Bundled transliterators:" in test_result.output
    assert "Example" in test_result.output

def test_dump_tests():
    runner = CliRunner()
    test_result = runner.invoke(cli.main, ["dump-tests", "Example"]) # yaml
    assert "a: A" in test_result.output
    test_result = runner.invoke(cli.main, ["dump-tests", "--to", "json", "Example"]) # json
    assert '"a": "A"' in test_result.output, test_result.output
    test_result = runner.invoke(cli.main, ["dump-tests", "--to", "yaml", "Example"]) # json
    assert "a: A" in test_result.output

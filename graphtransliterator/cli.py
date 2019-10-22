# -*- coding: utf-8 -*-

"""Console script for graphtransliterator."""

from graphtransliterator import GraphTransliterator
import click
import json
import os
import sys


@click.group()
def main():
    pass


def load_transliterator(source, **kwargs):
    """Loads transliterator (format, parameter)."""
    format, parameter = source
    if format == "bundled":
        mod = __import__("graphtransliterator.transliterators")
        transliterators_mod = mod.transliterators
        transliterator_class = getattr(transliterators_mod, parameter)
        return transliterator_class(**kwargs)

    elif format == "json":
        return GraphTransliterator.loads(parameter, **kwargs)
    elif format == "json_file":
        with open(parameter, "r") as f:
            return GraphTransliterator.loads(f.read(), **kwargs)
    elif format == "yaml_file":
        return GraphTransliterator.from_yaml_file(parameter, **kwargs)


@click.command()
@click.option(
    "--from",
    "-f",
    "from_",
    type=(click.Choice(["bundled", "json", "json_file", "yaml_file"]), str),
    help=(
        "Format (bundled/json/json_file/yaml_file) and "
        "source (name, JSON, or filename) of transliterator"
    ),
    nargs=2,
    required=True,
)
@click.option(
    "--to",
    "-t",
    type=click.Choice(["json", "python"]),
    help="Output format",
    nargs=1,
    required=False,
    show_default=True,
    default="python",
)
@click.option(
    "--check-ambiguity/--no-check-ambiguity",
    "-ca/-nca",
    default=False,
    help="Check for ambiguity.",
    show_default=True,
)
@click.option(
    "--ignore-errors/--no-ignore-errors",
    "-ie",
    "-nie",
    help="Ignore errors.",
    show_default=True,
    default=False,
)
@click.argument("input", nargs=-1)
def transliterate(from_, to, input, check_ambiguity, ignore_errors):
    """Transliterate INPUT."""
    transliterator = load_transliterator(
        from_, check_ambiguity=check_ambiguity, ignore_errors=ignore_errors
    )
    if len(input) == 1:
        output = transliterator.transliterate(input[0])
    else:
        output = [transliterator.transliterate(_) for _ in input]
    if to == "json":
        click.echo(json.dumps(output))
    else:
        click.echo(output)


@click.command()
@click.option(
    "--from",
    "-f",
    "from_",
    type=(click.Choice(["bundled", "yaml_file"]), str),
    help="Format (bundled/yaml_file) and source (name or filename) of transliterator",
    nargs=2,
    required=True,
)
@click.option(
    "--check-ambiguity/--no-check-ambiguity",
    "-ca/-nca",
    default=False,
    help="Check for ambiguity.",
    show_default=True,
)
def dump(from_, check_ambiguity):
    """Dump transliterator as JSON."""
    transliterator = load_transliterator(from_, check_ambiguity=check_ambiguity)
    click.echo(transliterator.dumps())


@click.command()
@click.option(
    "--from",
    "-f",
    "from_",
    type=(click.Choice(["bundled", "json", "json_file", "yaml_file"]), str),
    help=(
        "Format (bundled/json/json_file/yaml_file) and "
        "source (name, JSON, or filename) of transliterator"
    ),
    nargs=2,
    required=True,
)
@click.option(
    "--check-ambiguity/--no-check-ambiguity",
    "-ca/-nca",
    default=False,
    help="Check for ambiguity.",
    show_default=True,
)
def generate_tests(from_, check_ambiguity):
    """Generate tests as YAML."""
    import graphtransliterator.transliterators  # pragma: no cover
    transliterator = load_transliterator(from_, check_ambiguity=check_ambiguity)
    yaml_tests = graphtransliterator.transliterators.Bundled.generate_yaml_tests(
        transliterator
    )
    click.echo(yaml_tests)


@click.command()
@click.option(
    "--check-ambiguity/--no-check-ambiguity",
    "-ca/-nca",
    default=False,
    help="Check for ambiguity.",
    show_default=True,
)
@click.argument("bundled", nargs=1)
def test(bundled, check_ambiguity):
    """Test BUNDLED transliterator."""
    transliterator = load_transliterator(
        ["bundled", bundled], check_ambiguity=check_ambiguity
    )
    click.echo(transliterator.run_yaml_tests())


@click.argument("bundled", nargs=1)
@click.command()
def make_json(bundled):
    """Make JSON rules of BUNDLED transliterator."""
    import graphtransliterator.transliterators as transliterators  # pragma: no cover
    transliterator_class = getattr(transliterators, bundled)
    transliterator = transliterator_class.new(method="yaml")
    json_filename = os.path.join(
        transliterator.directory, transliterator.name + ".json"
    )
    with open(json_filename, "w") as f:
        f.write(transliterator.dumps())


main.add_command(transliterate)
main.add_command(dump)
main.add_command(generate_tests)
main.add_command(test)
main.add_command(make_json)

if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover

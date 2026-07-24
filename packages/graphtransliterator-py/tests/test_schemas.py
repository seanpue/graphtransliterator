import pytest
from graphtransliterator.schemas import GraphTransliteratorSchema
from marshmallow.exceptions import ValidationError


def test_schema_invalid_fields():
    schema = GraphTransliteratorSchema()

    # Test invalid rules format (e.g. non-list rules or bad token format)
    with pytest.raises(ValidationError):
        schema.load(
            {
                "tokens": {"a": "not-a-list"},  # Should be a list
                "rules": [],
                "whitespace": {"default": " ", "token_class": "wb", "consolidate": True},
            }
        )

    # Test invalid whitespace configuration
    with pytest.raises(ValidationError):
        schema.load(
            {
                "tokens": {"a": ["c1"]},
                "rules": [],
                "whitespace": {"default": " ", "token_class": "missing_class", "consolidate": True},
            }
        )

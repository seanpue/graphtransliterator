from marshmallow import fields, Schema


class MetadataSchema(Schema):
    """Schema for Bundled metadata."""

    name = fields.Str(required=True)
    description = fields.Str(required=True)
    version = fields.Str(required=True)
    url = fields.Url(required=False)
    author = fields.Str(required=False)
    author_email = fields.Email(required=False)
    maintainer = fields.Str(required=False)
    maintainer_email = fields.Email(required=False)
    license = fields.Str(required=False)
    keywords = fields.List(fields.Str(), required=False)
    project_urls = fields.Dict(keys=fields.Str(), values=fields.Url, required=False)

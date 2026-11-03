from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class CamelModel(BaseModel):
    """Base schema: snake_case in Python, camelCase in JSON (matches spec examples)."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, extra="forbid")

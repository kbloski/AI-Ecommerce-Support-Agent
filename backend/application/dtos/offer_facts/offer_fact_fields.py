from pydantic import BaseModel, ConfigDict, Field


class FactFields(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    name: str = Field(min_length=1, max_length=255)
    description: str = Field(min_length=1)
    evidence: str | None = None
    is_reviewed: bool = False

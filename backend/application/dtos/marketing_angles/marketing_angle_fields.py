from pydantic import BaseModel, Field, field_validator


class MarketingAngleFields(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str = Field(min_length=1)
    core_message: str
    value_proposition: str
    pain_point: str
    desire: str
    emotional_driver: str
    supporting_arguments: list[str]
    proof_points: list[str]

    @field_validator("name", "description")
    @classmethod
    def require_nonempty_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Text cannot be empty")
        return value


class MarketingAnglesResponse(BaseModel):
    angles: list[MarketingAngleFields]


class GenerateMarketingAnglesRequest(BaseModel):
    count: int = Field(default=3, ge=1, le=10)
    target_audience_ids: list[int] = Field(default_factory=list)
    generation_instructions: str = Field(default="", max_length=4000)


class UpdateMarketingAngleRequest(MarketingAngleFields):
    is_reviewed: bool = False

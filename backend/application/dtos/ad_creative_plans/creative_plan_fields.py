from pydantic import BaseModel, ConfigDict, Field, field_validator
from domain.enums.ad_formats import AdFormats


class CreativePlanFields(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=255)
    description: str = Field(min_length=1)
    format: AdFormats
    plan: str = Field(min_length=1)

    @field_validator("name", "description", "plan")
    @classmethod
    def require_text(cls, value):
        value = value.strip()
        if not value:
            raise ValueError("Text cannot be empty")
        return value


class CreativePlansResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    plans: list[CreativePlanFields]


class GenerateCreativePlansRequest(BaseModel):
    count: int = Field(default=1, ge=1, le=10)
    ad_concept_id: int | None = Field(default=None, gt=0)
    preferred_format: AdFormats | None = None
    ad_framework_id: str | None = Field(default=None, min_length=1, max_length=255)
    generation_instructions: str = Field(default="", max_length=4000)


class CreateCreativePlanRequest(CreativePlanFields):
    ad_concept_id: int | None = Field(default=None, gt=0)


class UpdateCreativePlanRequest(CreateCreativePlanRequest):
    is_reviewed: bool = False

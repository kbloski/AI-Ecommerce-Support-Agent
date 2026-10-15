from pydantic import BaseModel, Field, field_validator, model_validator

from domain.enums.ad_concept_mode import AdConceptMode
from domain.enums.ad_formats import AdFormats


class AdConceptFields(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str = Field(min_length=1)
    format: AdFormats
    core_idea: str = Field(min_length=1)
    key_message: str = Field(min_length=1)

    @field_validator("name", "description", "core_idea", "key_message")
    @classmethod
    def require_nonempty_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Text cannot be empty")
        return value


class AdConceptsResponse(BaseModel):
    concepts: list[AdConceptFields]


class AdConceptSelection(BaseModel):
    generation_mode: AdConceptMode = AdConceptMode.STANDARD
    marketing_angle_ids: list[int] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def accept_legacy_angle_id(cls, value):
        if isinstance(value, dict) and "marketing_angle_id" in value:
            value = dict(value)
            old_id = value.pop("marketing_angle_id")
            if "marketing_angle_ids" not in value:
                value["marketing_angle_ids"] = [] if old_id is None else [old_id]
        return value

    @model_validator(mode="after")
    def validate_selection(self):
        ids = self.marketing_angle_ids
        if any(id <= 0 for id in ids):
            raise ValueError("Marketing angle IDs must be positive")
        if len(ids) != len(set(ids)):
            raise ValueError("Marketing angles must be unique")
        if self.generation_mode == AdConceptMode.STANDARD and len(ids) > 1:
            raise ValueError("Standard mode supports at most one marketing angle")
        if self.generation_mode == AdConceptMode.EXPERIMENTAL and not ids:
            raise ValueError("Experimental mode requires at least one marketing angle")
        return self


class GenerateAdConceptsRequest(AdConceptSelection):
    count: int = Field(default=3, ge=1, le=10)
    preferred_format: AdFormats | None = None
    generation_instructions: str = Field(default="", max_length=4000)


class CreateAdConceptRequest(AdConceptFields, AdConceptSelection):
    pass


class UpdateAdConceptRequest(CreateAdConceptRequest):
    is_reviewed: bool = False

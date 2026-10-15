from typing import Literal

from pydantic import BaseModel, Field, field_validator


class AdConceptFields(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str = Field(min_length=1)
    format: Literal["video", "image"]
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


class GenerateAdConceptsRequest(BaseModel):
    count: int = Field(default=3, ge=1, le=10)
    marketing_angle_id: int | None = Field(default=None, gt=0)
    generation_instructions: str = Field(default="", max_length=4000)


class CreateAdConceptRequest(AdConceptFields):
    marketing_angle_id: int | None = Field(default=None, gt=0)


class UpdateAdConceptRequest(AdConceptFields):
    marketing_angle_id: int | None = Field(default=None, gt=0)
    is_reviewed: bool = False

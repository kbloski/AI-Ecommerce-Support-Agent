from pydantic import BaseModel, Field, field_validator


class GenerateUgcRequest(BaseModel):
    count: int = Field(default=3, ge=1, le=10)
    generation_instructions: str = Field(default="", max_length=4000)


class UgcGenerationFields(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    customer_persona: dict[str, str] = Field(default_factory=dict)
    content_format: str = ""
    angle: str = ""
    hook_idea: str = ""
    video_flow: list[str] = Field(default_factory=list)
    recording_style: str = ""
    platform_fit: list[str] = Field(default_factory=list)
    cta: str = ""
    why_it_should_work: str = ""

    @field_validator("name")
    @classmethod
    def nonempty_name(cls, value):
        value = value.strip()
        if not value:
            raise ValueError("Name cannot be blank")
        return value


class UgcGenerationResponse(BaseModel):
    ugc_creatives: list[UgcGenerationFields]

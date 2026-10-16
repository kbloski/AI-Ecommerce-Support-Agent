from pydantic import BaseModel, ConfigDict, Field, field_validator


class AdCopyFields(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=1, max_length=255)
    primary_text: str = Field(min_length=1)
    headline: str = Field(min_length=1)
    description: str = Field(min_length=1)
    cta: str | None = None

    @field_validator("name", "primary_text", "headline", "description")
    @classmethod
    def require_text(cls, value):
        value = value.strip()
        if not value:
            raise ValueError("Text cannot be blank")
        return value

    @field_validator("cta")
    @classmethod
    def optional_cta(cls, value):
        return (value.strip() or None) if value is not None else None


class GenerateAdCopyRequest(BaseModel):
    count: int = Field(default=3, ge=1, le=10)
    generation_instructions: str = Field(default="", max_length=4000)


class AdCopiesResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    copies: list[AdCopyFields]

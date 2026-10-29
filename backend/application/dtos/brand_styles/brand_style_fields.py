from pydantic import BaseModel, ConfigDict, Field, field_validator


HEX_COLOR_PATTERN = r"^#[0-9A-Fa-f]{6}$"


class BrandStyleFields(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    font_family: str = Field(min_length=1, max_length=255)
    brand_color: str = Field(pattern=HEX_COLOR_PATTERN)
    text_color: str = Field(pattern=HEX_COLOR_PATTERN)
    background_color: str = Field(pattern=HEX_COLOR_PATTERN)

    @field_validator("brand_color", "text_color", "background_color")
    @classmethod
    def normalize_color(cls, value):
        return value.upper()


class GenerateBrandStyleRequest(BaseModel):
    generation_instructions: str = Field(default="", max_length=4000)

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class GeneratePageRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    page_blueprint_id: int | None = Field(default=None, gt=0, strict=True)
    generation_instructions: str = Field(default="", max_length=4000)


class GeneratedPageSection(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: str = Field(min_length=1, max_length=100)
    name: str = Field(min_length=1, max_length=255)
    content: str = Field(min_length=1, max_length=20000)
    position: int = Field(ge=1, strict=True)

    @field_validator("type", "name", "content")
    @classmethod
    def nonblank(cls, value):
        value = value.strip()
        if not value:
            raise ValueError("Text cannot be blank")
        return value


class GeneratedPage(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=255)
    description: str = Field(default="", max_length=4000)
    sections: list[GeneratedPageSection] = Field(min_length=1, max_length=50)

    @field_validator("name")
    @classmethod
    def nonblank_name(cls, value):
        value = value.strip()
        if not value:
            raise ValueError("Name cannot be blank")
        return value

    @model_validator(mode="after")
    def ordered_sections(self):
        if sorted(section.position for section in self.sections) != list(range(1, len(self.sections) + 1)):
            raise ValueError("Section positions must be unique and contiguous starting at 1")
        return self

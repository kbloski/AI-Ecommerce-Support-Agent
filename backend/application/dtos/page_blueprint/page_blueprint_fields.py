from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from domain.enums.page_type import PageType


class PageBlueprintSectionFields(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: str = Field(min_length=1, max_length=100)
    name: str = Field(min_length=1, max_length=255)
    purpose: str = Field(min_length=1, max_length=4000)
    position: int = Field(ge=1, strict=True)
    is_optional: bool = False

    @field_validator("type", "name", "purpose")
    @classmethod
    def nonempty_text(cls, value):
        value = value.strip()
        if not value:
            raise ValueError("Text cannot be blank")
        return value


class PageBlueprintSectionInput(PageBlueprintSectionFields):
    id: int | None = Field(default=None, gt=0, strict=True)


class PageBlueprintFields(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=255)
    description: str = Field(default="", max_length=4000)
    sections: list[PageBlueprintSectionInput] = Field(min_length=1, max_length=50)

    @field_validator("name")
    @classmethod
    def nonempty_name(cls, value):
        value = value.strip()
        if not value:
            raise ValueError("Name cannot be blank")
        return value

    @model_validator(mode="after")
    def validate_section_order_and_ids(self):
        if sorted(section.position for section in self.sections) != list(range(1, len(self.sections) + 1)):
            raise ValueError("Section positions must be unique and contiguous starting at 1")
        ids = [section.id for section in self.sections if section.id is not None]
        if len(ids) != len(set(ids)):
            raise ValueError("Section IDs must be unique")
        return self


class GeneratePageBlueprintRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    page_type: PageType | None = None
    section_count: int | None = Field(default=8, ge=1, le=50, strict=True)
    generation_instructions: str = Field(default="", max_length=4000)


class PageBlueprintGenerationResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=255)
    description: str = Field(default="", max_length=4000)
    sections: list[PageBlueprintSectionFields] = Field(min_length=1, max_length=50)

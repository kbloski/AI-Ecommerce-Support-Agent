from pydantic import BaseModel, ConfigDict, Field

from domain.enums.context_type import ContextType


class ChatContext(BaseModel):
    """Resource selection, the same as in the resource export."""
    model_config = ConfigDict(extra="forbid")

    type: ContextType
    id: int = Field(gt=0)
    include: list[ContextType] = []
    target_audience_ids: list[int] = []
    marketing_angle_ids: list[int] = []
    ad_concept_ids: list[int] = []
    creative_plan_ids: list[int] = []
    ugc_creative_ids: list[int] = []
    ad_copy_ids: list[int] = []
    brand_style_ids: list[int] = []
    analysis_ids: list[int] = []
    checklist_ids: list[int] = []
    page_blueprint_ids: list[int] = []
    page_ids: list[int] = []
    note_ids: list[int] = []
    include_offer_facts: bool = True
    include_additional_contexts: bool = True


class CreateConversationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    title: str = Field(default="", max_length=255)
    context: ChatContext


class UpdateConversationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    title: str | None = Field(default=None, min_length=1, max_length=255)
    context: ChatContext | None = None


class SendMessageRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    content: str = Field(min_length=1, max_length=20000)

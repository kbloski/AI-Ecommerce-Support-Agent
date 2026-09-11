from typing import Optional, List

from common.mixins.json_serializable import JSONSerializable


class UgcCreativeDto(JSONSerializable):

    def __init__(
        self,
        id: int,
        message_strategy_id: int,
        name: Optional[str],
        customer_persona: Optional[dict],
        content_format: Optional[str],
        angle: Optional[str],
        hook_idea: Optional[str],
        video_flow: Optional[List[str]],
        recording_style: Optional[str],
        platform_fit: Optional[List[str]],
        cta: Optional[str],
        why_it_should_work: Optional[str],
        is_reviewed: bool,
    ):
        self.id = id
        self.message_strategy_id = message_strategy_id
        self.name = name
        self.customer_persona = customer_persona
        self.content_format = content_format
        self.angle = angle
        self.hook_idea = hook_idea
        self.video_flow = video_flow
        self.recording_style = recording_style
        self.platform_fit = platform_fit
        self.cta = cta
        self.why_it_should_work = why_it_should_work
        self.is_reviewed = is_reviewed

    def to_dict(self, exclude=None):
        exclude = set(exclude or [])

        data = {
            "id": self.id,
            "message_strategy_id": self.message_strategy_id,
            "name": self.name,
            "customer_persona": self.customer_persona,
            "content_format": self.content_format,
            "angle": self.angle,
            "hook_idea": self.hook_idea,
            "video_flow": self.video_flow,
            "recording_style": self.recording_style,
            "platform_fit": self.platform_fit,
            "cta": self.cta,
            "why_it_should_work": self.why_it_should_work,
            "is_reviewed": self.is_reviewed,
        }

        return {k: v for k, v in data.items() if k not in exclude}

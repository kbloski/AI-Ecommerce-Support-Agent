from typing import Optional

from application.dtos.ads.ad_framework_dto import AdFrameworkDto
from application.dtos.ads.creative_angle_dto import CreativeAngleDto
from application.dtos.ads.execution_style_dto import ExecutionStyleDto
from common.mixins.json_serializable import JSONSerializable


class CreativeExecutionSetupDto(JSONSerializable):
    def __init__(
        self,
        id: int,
        ad_setup_id: int,
        name: str,
        duration_seconds: Optional[int],
        number_of_slides: Optional[int],
        ad_framework_id: Optional[str],
        creative_angle_id: Optional[str],
        execution_style_id: Optional[str],
        additional_instructions: Optional[str],
        ad_framework: Optional[AdFrameworkDto] = None,
        creative_angle: Optional[CreativeAngleDto] = None,
        execution_style: Optional[ExecutionStyleDto] = None,
    ):
        self.id = id
        self.ad_setup_id = ad_setup_id
        self.name = name
        self.duration_seconds = duration_seconds
        self.number_of_slides = number_of_slides
        self.ad_framework_id = ad_framework_id
        self.creative_angle_id = creative_angle_id
        self.execution_style_id = execution_style_id
        self.additional_instructions = additional_instructions
        self.ad_framework = ad_framework
        self.creative_angle = creative_angle
        self.execution_style = execution_style

    def to_dict(self, exclude=None):
        exclude = set(exclude or [])
        data = {
            "id": self.id,
            "ad_setup_id": self.ad_setup_id,
            "name": self.name,
            "duration_seconds": self.duration_seconds,
            "number_of_slides": self.number_of_slides,
            "ad_framework_id": self.ad_framework_id,
            "creative_angle_id": self.creative_angle_id,
            "execution_style_id": self.execution_style_id,
            "additional_instructions": self.additional_instructions,
            "ad_framework": self.ad_framework.to_dict() if self.ad_framework else None,
            "creative_angle": self.creative_angle.to_dict() if self.creative_angle else None,
            "execution_style": self.execution_style.to_dict() if self.execution_style else None,
        }
        return {key: value for key, value in data.items() if key not in exclude}

    def to_content_dict(self):
        return {
            "name": self.name,
            "duration_seconds": self.duration_seconds,
            "number_of_slides": self.number_of_slides,
            "additional_instructions": self.additional_instructions,
            "ad_framework": (
                self.ad_framework.to_content_dict() if self.ad_framework else None
            ),
            "creative_angle": (
                self.creative_angle.to_content_dict() if self.creative_angle else None
            ),
            "execution_style": (
                self.execution_style.to_content_dict() if self.execution_style else None
            ),
        }

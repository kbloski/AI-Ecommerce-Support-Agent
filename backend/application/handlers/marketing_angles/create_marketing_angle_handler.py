from fastapi import HTTPException

from application.dtos.marketing_angles.marketing_angle_fields import MarketingAngleFields
from application.mappers.marketing_angle_mapper import marketing_angle_to_dict
from di.container import Container
from domain.models.offer.marketing_angle import MarketingAngle


def create_marketing_angle_handler(offer_profile_id: int, fields: MarketingAngleFields):
    container = Container()
    if container.offer_profiles_repository().get_by_id(offer_profile_id) is None:
        raise HTTPException(404, "Offer profile not found")
    item = MarketingAngle(offer_profile_id=offer_profile_id, **fields.model_dump())
    return marketing_angle_to_dict(container.marketing_angles_repository().create_many([item])[0])

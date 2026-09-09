from domain.models.brand_marketing.brand_marketing import BrandMarketing
from application.dtos.brand_marketing.brand_marketing_response_dto import BrandMarketingDto


class BrandMarketingMapper:

    @staticmethod
    def to_dto(item: BrandMarketing) -> BrandMarketingDto:
        return BrandMarketingDto(
            id=item.id,
            offer_profile_id=item.offer_profile_id,
            brand_name=item.brand_name,
            brand_positioning=item.brand_positioning,
            brand_category=item.brand_category,
            brand_target_customer=item.brand_target_customer,
            brand_competitive_difference=item.brand_competitive_difference,
            brand_purpose=item.brand_purpose,
            brand_promise=item.brand_promise,
            brand_personality=item.brand_personality,
            brand_values=item.brand_values,
            brand_voice=item.brand_voice,
            brand_tone=item.brand_tone,
            brand_tone_social_media=item.brand_tone_social_media,
            brand_tone_customer_communication=item.brand_tone_customer_communication,
            tagline=item.tagline,
            unique_selling_proposition=item.unique_selling_proposition,
            key_messages=item.key_messages,
            target_perception=item.target_perception,
            target_emotions=item.target_emotions,
            brand_associations=item.brand_associations,
            customer_desires=item.customer_desires,
            customer_pains=item.customer_pains,
            customer_fears=item.customer_fears,
            customer_objections=item.customer_objections,
            purchase_motivators=item.purchase_motivators,
            brand_story=item.brand_story,
            brand_story_angle=item.brand_story_angle,
            customer_transformation=item.customer_transformation,
            content_pillars=item.content_pillars,
            storytelling_angles=item.storytelling_angles,
            ugc_direction=item.ugc_direction,
            visual_style=item.visual_style,
            visual_direction=item.visual_direction,
            brand_always_do=item.brand_always_do,
            brand_never_do=item.brand_never_do,
        )

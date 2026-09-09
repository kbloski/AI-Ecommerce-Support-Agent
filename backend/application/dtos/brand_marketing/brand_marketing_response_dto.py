from typing import Optional, List

from common.mixins.json_serializable import JSONSerializable


class BrandMarketingDto(JSONSerializable):

    def __init__(
        self,
        id: int,
        offer_profile_id: int,
        brand_name: Optional[str],
        brand_positioning: Optional[str],
        brand_category: Optional[str],
        brand_target_customer: Optional[str],
        brand_competitive_difference: Optional[str],
        brand_purpose: Optional[str],
        brand_promise: Optional[str],
        brand_personality: Optional[List[str]],
        brand_values: Optional[List[str]],
        brand_voice: Optional[str],
        brand_tone: Optional[str],
        brand_tone_social_media: Optional[str],
        brand_tone_customer_communication: Optional[str],
        tagline: Optional[str],
        unique_selling_proposition: Optional[str],
        key_messages: Optional[List[str]],
        target_perception: Optional[List[str]],
        target_emotions: Optional[List[str]],
        brand_associations: Optional[List[str]],
        customer_desires: Optional[List[str]],
        customer_pains: Optional[List[str]],
        customer_fears: Optional[List[str]],
        customer_objections: Optional[List[str]],
        purchase_motivators: Optional[List[str]],
        brand_story: Optional[str],
        brand_story_angle: Optional[str],
        customer_transformation: Optional[str],
        content_pillars: Optional[List[str]],
        storytelling_angles: Optional[List[str]],
        ugc_direction: Optional[List[str]],
        visual_style: Optional[str],
        visual_direction: Optional[str],
        brand_always_do: Optional[List[str]],
        brand_never_do: Optional[List[str]],
    ):
        self.id = id
        self.offer_profile_id = offer_profile_id
        self.brand_name = brand_name
        self.brand_positioning = brand_positioning
        self.brand_category = brand_category
        self.brand_target_customer = brand_target_customer
        self.brand_competitive_difference = brand_competitive_difference
        self.brand_purpose = brand_purpose
        self.brand_promise = brand_promise
        self.brand_personality = brand_personality
        self.brand_values = brand_values
        self.brand_voice = brand_voice
        self.brand_tone = brand_tone
        self.brand_tone_social_media = brand_tone_social_media
        self.brand_tone_customer_communication = brand_tone_customer_communication
        self.tagline = tagline
        self.unique_selling_proposition = unique_selling_proposition
        self.key_messages = key_messages
        self.target_perception = target_perception
        self.target_emotions = target_emotions
        self.brand_associations = brand_associations
        self.customer_desires = customer_desires
        self.customer_pains = customer_pains
        self.customer_fears = customer_fears
        self.customer_objections = customer_objections
        self.purchase_motivators = purchase_motivators
        self.brand_story = brand_story
        self.brand_story_angle = brand_story_angle
        self.customer_transformation = customer_transformation
        self.content_pillars = content_pillars
        self.storytelling_angles = storytelling_angles
        self.ugc_direction = ugc_direction
        self.visual_style = visual_style
        self.visual_direction = visual_direction
        self.brand_always_do = brand_always_do
        self.brand_never_do = brand_never_do

    def to_dict(self, exclude=None):
        exclude = set(exclude or [])

        data = {
            "id": self.id,
            "offer_profile_id": self.offer_profile_id,
            "brand_name": self.brand_name,
            "brand_positioning": self.brand_positioning,
            "brand_category": self.brand_category,
            "brand_target_customer": self.brand_target_customer,
            "brand_competitive_difference": self.brand_competitive_difference,
            "brand_purpose": self.brand_purpose,
            "brand_promise": self.brand_promise,
            "brand_personality": self.brand_personality,
            "brand_values": self.brand_values,
            "brand_voice": self.brand_voice,
            "brand_tone": self.brand_tone,
            "brand_tone_social_media": self.brand_tone_social_media,
            "brand_tone_customer_communication": self.brand_tone_customer_communication,
            "tagline": self.tagline,
            "unique_selling_proposition": self.unique_selling_proposition,
            "key_messages": self.key_messages,
            "target_perception": self.target_perception,
            "target_emotions": self.target_emotions,
            "brand_associations": self.brand_associations,
            "customer_desires": self.customer_desires,
            "customer_pains": self.customer_pains,
            "customer_fears": self.customer_fears,
            "customer_objections": self.customer_objections,
            "purchase_motivators": self.purchase_motivators,
            "brand_story": self.brand_story,
            "brand_story_angle": self.brand_story_angle,
            "customer_transformation": self.customer_transformation,
            "content_pillars": self.content_pillars,
            "storytelling_angles": self.storytelling_angles,
            "ugc_direction": self.ugc_direction,
            "visual_style": self.visual_style,
            "visual_direction": self.visual_direction,
            "brand_always_do": self.brand_always_do,
            "brand_never_do": self.brand_never_do,
        }

        return {k: v for k, v in data.items() if k not in exclude}

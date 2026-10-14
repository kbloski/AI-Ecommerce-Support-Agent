from application.dtos.offer_profiles.offer_profile_dto import OfferProfileDto

def offer_profile_to_dict(profile):
    return {key: getattr(profile, key) for key in ("id", "offer_source_id", "name", "created_at")}


class OfferProfileMapper:
    @staticmethod
    def to_dto(profile):
        return OfferProfileDto(**offer_profile_to_dict(profile))

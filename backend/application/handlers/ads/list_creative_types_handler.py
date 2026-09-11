from domain.enums.creative_types import CreativeTypes


def list_creative_types_handler():
    return [
        {"id": creative_type.value, "name": creative_type.value.capitalize()}
        for creative_type in CreativeTypes
    ]

from di.container import Container
from domain.enums.enums import CreativeTypes
from domain.models.creative_execution_setup.creative_execution_setup import CreativeExecutionSetup


def create_creative_execution_setup_handler(ad_setup_id: int, fields: dict):
    container = Container()
    ad_setup = container.ad_setup_service().get_ad_setup_by_id(ad_setup_id)

    references = (
        ("ad_framework_id", container.ad_framework_service()),
        ("creative_angle_id", container.creative_angle_service()),
        ("execution_style_id", container.execution_style_service()),
    )
    for field, service in references:
        reference_id = fields.get(field)
        if reference_id and service.build_llm_context(reference_id) is None:
            raise ValueError(f"Unknown {field}: {reference_id}")

    duration_seconds = fields.get("duration_seconds")
    number_of_slides = fields.get("number_of_slides")
    if ad_setup.creative_type == CreativeTypes.VIDEO.value:
        number_of_slides = None
        duration_seconds = duration_seconds or 15
    elif ad_setup.creative_type == CreativeTypes.CAROUSEL.value:
        duration_seconds = None
        number_of_slides = number_of_slides or 5
    else:
        duration_seconds = None
        number_of_slides = None

    item = CreativeExecutionSetup(
        ad_setup_id=ad_setup_id,
        name=fields.get("name") or "Default setup",
        duration_seconds=duration_seconds,
        number_of_slides=number_of_slides,
        ad_framework_id=fields.get("ad_framework_id"),
        creative_angle_id=fields.get("creative_angle_id"),
        execution_style_id=fields.get("execution_style_id"),
        additional_instructions=fields.get("additional_instructions"),
    )
    return container.creative_execution_setup_service().create(item)

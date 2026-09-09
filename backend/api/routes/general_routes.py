from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import AnyHttpUrl, BaseModel, Field
from domain.enums.fact_status import FactStatus
from domain.enums.review_status import ReviewStatus

from application.handlers.ads.list_ad_frameworks_handler import list_ad_frameworks_handler
from application.handlers.ads.list_creative_angels_handler import list_creative_angels_handler
from application.handlers.ads.list_execution_styles_handler import list_execution_styles_handler
from application.handlers.ads.list_platforms_handler import list_platforms_handler
from application.handlers.ads.list_fact_statuses_handler import list_fact_statuses_handler
from application.handlers.ads.list_review_statuses_handler import list_review_statuses_handler
from application.handlers.offers.get_offers import get_offers
from application.handlers.offers.create_offer import create_offer
from application.handlers.offers.get_offer import get_offer_handler
from application.handlers.offers.delete_offer import delete_offer_handler
from application.handlers.offer_profiles.offer_profile_generate import offer_profile_generate_handler
from application.handlers.offer_profiles.get_offer_profile_handler import get_offer_profile_handler
from application.handlers.offer_profiles.get_offer_profiles_handler import get_offer_profiles_handler
from application.handlers.offer_profiles.delete_offer_profile_handler import delete_offer_profile_handler
from application.handlers.offer_profiles.list_offer_profile_elements_handler import list_offer_profile_elements_handler
from application.handlers.offer_profiles.create_offer_profile_element_handler import create_offer_profile_element_handler
from application.handlers.offer_profiles.generate_offer_profile_elements_handler import generate_offer_profile_elements_handler
from application.handlers.offer_profiles.update_offer_profile_element_handler import update_offer_profile_element_handler
from application.handlers.offer_profiles.delete_offer_profile_element_handler import delete_offer_profile_element_handler
from application.handlers.offer_profiles.list_offer_profile_element_types_handler import list_offer_profile_element_types_handler
from application.handlers.offers.update_offer_handler import update_offer_handler
from application.handlers.offer_profiles.update_offer_profile_handler import update_offer_profile_handler
from application.handlers.brand_marketing.update_brand_marketing_handler import update_brand_marketing_handler
from application.handlers.marketing_strategy.update_marketing_strategy_handler import update_marketing_strategy_handler
from application.handlers.offer_strategy.update_offer_strategy_handler import update_offer_strategy_handler
from application.handlers.page_strategy.update_page_strategy_handler import update_page_strategy_handler
from application.handlers.page_blueprint.update_page_blueprint_handler import update_page_blueprint_handler
from application.handlers.page_content_plan.update_page_content_plan_handler import update_page_content_plan_handler
from application.handlers.page_copy.update_page_copy_handler import update_page_copy_handler
from application.handlers.ad_strategy.update_ad_strategy_handler import update_ad_strategy_handler
from application.handlers.creative_strategy.update_creative_strategy_handler import update_creative_strategy_handler
from application.handlers.ad_execution.update_ad_execution_handler import update_ad_execution_handler
from application.handlers.creative_execution.update_creative_execution_handler import update_creative_execution_handler
from application.handlers.target_audience.generate_target_audience_handler import generate_target_audience_handler
from application.handlers.target_audience.get_target_audience_handler import get_target_audience_handler
from application.handlers.target_audience.get_target_audience_preview_handler import get_target_audience_preview_handler
from application.handlers.target_audience.delete_target_audience_handler import delete_target_audience_handler
from application.handlers.target_audience.update_target_audience_handler import update_target_audience_handler
# from application.handlers.offers.suggest_offer_profile_data_handler import suggest_offer_profile_data_handler
from application.handlers.analysis.offer_profile_analysis_answers_generate_handler import offer_profile_analysis_answers_generate_handler
from application.handlers.analysis.create_analysis_for_offer_profile_handler import create_analysis_for_offer_profile_handler
from application.handlers.analysis.get_analysis_by_id_hanlder import get_analysis_by_id_handler
from application.handlers.analysis.get_analysis_for_offer_profile_hanlder import get_analysis_for_offer_profile_handler
from application.handlers.analysis.analyse_checklist_generate_handler import analyse_checklist_generate_handler
from application.handlers.analysis.delete_analysis_handler import delete_analysis_handler
from application.handlers.analysis.delete_analysis_question_handler import delete_analysis_question_handler
from application.handlers.checklist.create_checklist_for_analysis_handler import create_checklist_for_analysis_handler
from application.handlers.checklist.get_analysis_checklists_handler import get_analyse_checklists_handler
from application.handlers.checklist.get_checklist_by_id_handler import get_checklist_by_id_handler
from application.handlers.checklist.delete_checklist_item_handler import delete_checklist_item_handler
from application.handlers.checklist.delete_checklist_handler import delete_checklist_handler
from application.handlers.advertisement.offer_profile_advertisement_generate_handler import offer_profile_advertisement_generate_handler
from application.handlers.brand_marketing.generate_brand_marketing_handler import generate_brand_marketing_handler
from application.handlers.brand_marketing.get_brand_marketing_handler import get_brand_marketing_handler
from application.handlers.brand_marketing.get_offer_profile_brand_marketings_handler import get_offer_profile_brand_marketings_handler
from application.handlers.brand_marketing.delete_brand_marketing_handler import delete_brand_marketing_handler
from application.handlers.marketing_strategy.generate_marketing_strategy_handler import generate_marketing_strategy_handler
from application.handlers.marketing_strategy.get_marketing_strategy_handler import get_marketing_strategy_handler
from application.handlers.marketing_strategy.get_brand_marketing_marketing_strategies_handler import get_brand_marketing_marketing_strategies_handler
from application.handlers.marketing_strategy.delete_marketing_strategy_handler import delete_marketing_strategy_handler
from application.handlers.offer_strategy.generate_offer_strategy_handler import generate_offer_strategy_handler
from application.handlers.offer_strategy.get_offer_strategy_handler import get_offer_strategy_handler
from application.handlers.offer_strategy.get_marketing_strategy_offer_strategies_handler import get_marketing_strategy_offer_strategies_handler
from application.handlers.offer_strategy.delete_offer_strategy_handler import delete_offer_strategy_handler
from application.handlers.message_strategy.generate_message_strategy_handler import generate_message_strategy_handler
from application.handlers.message_strategy.get_message_strategy_handler import get_message_strategy_handler
from application.handlers.message_strategy.get_offer_strategy_message_strategies_handler import get_offer_strategy_message_strategies_handler
from application.handlers.message_strategy.delete_message_strategy_handler import delete_message_strategy_handler
from application.handlers.message_strategy.update_message_strategy_handler import update_message_strategy_handler
from application.handlers.page_strategy.generate_page_strategy_json_handler import generate_page_strategy_json_handler
from application.handlers.ad_strategy.generate_ad_strategy_handler import generate_ad_strategy_handler
from application.handlers.ad_strategy.get_ad_strategy_handler import get_ad_strategy_handler
from application.handlers.ad_strategy.get_message_strategy_ad_strategies_handler import get_message_strategy_ad_strategies_handler
from application.handlers.ad_strategy.delete_ad_strategy_handler import delete_ad_strategy_handler
from application.handlers.creative_strategy.generate_creative_strategy_handler import generate_creative_strategy_handler
from application.handlers.ad_execution.create_ad_execution_handler import create_ad_execution_handler
from application.handlers.ad_execution.get_ad_execution_handler import get_ad_execution_handler
from application.handlers.ad_execution.get_creative_strategy_ad_executions_handler import get_creative_strategy_ad_executions_handler
from application.handlers.ad_execution.delete_ad_execution_handler import delete_ad_execution_handler
from application.handlers.creative_execution.generate_creative_execution_handler import generate_creative_execution_handler
from application.handlers.creative_execution.get_creative_execution_handler import get_creative_execution_handler
from application.handlers.creative_execution.get_ad_execution_creative_executions_handler import get_ad_execution_creative_executions_handler
from application.handlers.creative_execution.delete_creative_execution_handler import delete_creative_execution_handler
from application.handlers.creative_strategy.get_creative_strategy_handler import get_creative_strategy_handler
from application.handlers.creative_strategy.get_ad_strategy_creative_strategies_handler import get_ad_strategy_creative_strategies_handler
from application.handlers.creative_strategy.delete_creative_strategy_handler import delete_creative_strategy_handler
from application.handlers.ugc_creatives.generate_ugc_creatives_handler import generate_ugc_creatives_handler
from application.handlers.ugc_creatives.get_ugc_creative_handler import get_ugc_creative_handler
from application.handlers.ugc_creatives.get_message_strategy_ugc_creatives_handler import get_message_strategy_ugc_creatives_handler
from application.handlers.ugc_creatives.delete_ugc_creative_handler import delete_ugc_creative_handler
from application.handlers.page_strategy.get_page_strategy_handler import get_page_strategy_handler
from application.handlers.page_strategy.get_message_strategy_page_strategies_handler import get_message_strategy_page_strategies_handler
from application.handlers.page_strategy.delete_page_strategy_handler import delete_page_strategy_handler
from application.handlers.page_requirements.create_page_requirements_handler import create_page_requirements_handler
from application.handlers.page_requirements.get_page_requirements_handler import get_page_requirements_handler
from application.handlers.page_requirements.get_page_strategy_page_requirements_handler import get_page_strategy_page_requirements_handler
from application.handlers.page_requirements.update_page_requirements_handler import update_page_requirements_handler
from application.handlers.page_requirements.delete_page_requirements_handler import delete_page_requirements_handler
from application.handlers.page_blueprint.generate_page_blueprint_handler import generate_page_blueprint_handler
from application.handlers.page_blueprint.get_page_blueprint_handler import get_page_blueprint_handler
from application.handlers.page_blueprint.get_page_requirements_page_blueprints_handler import get_page_requirements_page_blueprints_handler
from application.handlers.page_blueprint.delete_page_blueprint_handler import delete_page_blueprint_handler
from application.handlers.ads.list_page_sections_handler import list_page_sections_handler
from application.handlers.page_content_plan.generate_page_content_plan_handler import generate_page_content_plan_handler
from application.handlers.page_content_plan.get_page_content_plan_handler import get_page_content_plan_handler
from application.handlers.page_content_plan.get_page_blueprint_page_content_plans_handler import get_page_blueprint_page_content_plans_handler
from application.handlers.page_content_plan.delete_page_content_plan_handler import delete_page_content_plan_handler
from application.handlers.page_copy.generate_page_copy_handler import generate_page_copy_handler
from application.handlers.page_copy.get_page_copy_handler import get_page_copy_handler
from application.handlers.page_copy.get_page_content_plan_page_copies_handler import get_page_content_plan_page_copies_handler
from application.handlers.page_copy.delete_page_copy_handler import delete_page_copy_handler
from application.handlers.settings.get_output_prompt_handler import get_output_prompt_handler
from application.handlers.settings.save_output_prompt_handler import save_output_prompt_handler
from application.handlers.settings.get_ollama_settings_handler import get_ollama_settings_handler
from application.handlers.settings.save_ollama_settings_handler import save_ollama_settings_handler
from application.handlers.settings.list_ollama_models_handler import list_ollama_models_handler
from application.handlers.pipeline.get_pipeline_path_handler import get_pipeline_path_handler
from domain.enums.pipeline_entity_type import PipelineEntityType
from domain.enums.offer_profile_element_type import OfferProfileElementType
from domain.enums.offer_profile_element_type import OfferProfileElementType


class SaveOutputPromptRequest(BaseModel):
    content: str


class UpdateFieldsRequest(BaseModel):
    fields: Dict[str, Any]


class OllamaSettingsFields(BaseModel):
    ollama_url: Optional[AnyHttpUrl] = None
    ollama_model: Optional[str] = None
    ollama_timeout: Optional[int] = Field(default=None, gt=0)
    ollama_context_length: Optional[int] = Field(default=None, gt=0)
    ollama_temperature: Optional[float] = Field(default=None, ge=0, le=2)


class SaveOllamaSettingsRequest(BaseModel):
    fields: OllamaSettingsFields


class PipelinePathRequest(BaseModel):
    entity_type: PipelineEntityType
    entity_id: int


class PageSectionRequirementInput(BaseModel):
    page_section_type_id: str
    requirement_type: str
    position: Optional[int] = None


class UpdatePageRequirementsRequest(BaseModel):
    section_requirements: List[PageSectionRequirementInput]


class UpdateTargetAudienceRequest(BaseModel):
    fact_status: Optional[FactStatus] = None
    review_status: Optional[ReviewStatus] = None
    name: Optional[str] = None
    reason: Optional[str] = None
    score: Optional[float] = None
    confidence: Optional[float] = None
    age_min: Optional[int] = None
    age_max: Optional[int] = None
    gender: Optional[str] = None
    location: Optional[str] = None
    purchasing_power: Optional[str] = None
    lifestyles: Optional[List[Any]] = None
    values: Optional[List[Any]] = None
    awareness_level: Optional[str] = None
    price_sensitivity: Optional[str] = None
    research_level: Optional[str] = None
    decision_time: Optional[str] = None
    pain_points: Optional[List[Any]] = None
    motivations: Optional[List[Any]] = None
    buying_triggers: Optional[List[Any]] = None
    objections: Optional[List[Any]] = None
    message_angles: Optional[List[Any]] = None
    marketing_channels: Optional[List[Any]] = None



class CreateOfferProfileElementRequest(BaseModel):
    type: OfferProfileElementType
    name: str = Field(min_length=1, max_length=255)
    description: Optional[str] = None


class GenerateOfferProfileElementsRequest(BaseModel):
    element_types: List[OfferProfileElementType] = Field(min_length=1)
    examples_per_type: int = 3


def register_general_routes(router: APIRouter):

    # -----------------------------
    # Legacy GET endpoints for routes moved to POST/DELETE above.
    # Kept only to return a clear 410 instead of silently mutating data via GET.
    # -----------------------------
    @router.get("/offers/{id}/offer-profiles/generate")
    def _legacy_get_0(id: str):
        raise HTTPException(status_code=410, detail="This endpoint now requires POST /offers/{id}/offer-profiles/generate")

    @router.get("/offer-profiles/{offer_profile_id}/target-audiences/generate")
    def _legacy_get_1(offer_profile_id: str):
        raise HTTPException(status_code=410, detail="This endpoint now requires POST /offer-profiles/{offer_profile_id}/target-audiences/generate")

    @router.get("/offer-profiles/{offer_profile_id}/analysis/{analyse_id}/answers/generate")
    def _legacy_get_2(offer_profile_id: str, analyse_id: str):
        raise HTTPException(status_code=410, detail="This endpoint now requires POST /offer-profiles/{offer_profile_id}/analysis/{analyse_id}/answers/generate")

    @router.get("/offer-profiles/{offer_profile_id}/analysis/{analyse_id}/checklists/{checklist_id}/generate")
    def _legacy_get_3(offer_profile_id: str, analyse_id: str, checklist_id: str):
        raise HTTPException(status_code=410, detail="This endpoint now requires POST /offer-profiles/{offer_profile_id}/analysis/{analyse_id}/checklists/{checklist_id}/generate")

    @router.get("/offer-profiles/{offer_profile_id}/brand-marketing/generate")
    def _legacy_get_4(offer_profile_id: str):
        raise HTTPException(status_code=410, detail="This endpoint now requires POST /offer-profiles/{offer_profile_id}/brand-marketing/generate")

    @router.get("/offer-profiles/{offer_profile_id}/brand-marketing/{brand_markeging_id}/marketing-strategy/generate")
    def _legacy_get_5(offer_profile_id: str, brand_markeging_id: str):
        raise HTTPException(status_code=410, detail="This endpoint now requires POST /offer-profiles/{offer_profile_id}/brand-marketing/{brand_markeging_id}/marketing-strategy/generate")

    @router.get("/marketing-strategy/{marketing_strategy_id}/offer-strategy/generate")
    def _legacy_get_6(marketing_strategy_id: str):
        raise HTTPException(status_code=410, detail="This endpoint now requires POST /marketing-strategy/{marketing_strategy_id}/offer-strategy/generate")

    @router.get("/offer-strategy/{offer_strategy_id}/message-strategy/generate")
    def _legacy_get_7(offer_strategy_id: str):
        raise HTTPException(status_code=410, detail="This endpoint now requires POST /offer-strategy/{offer_strategy_id}/message-strategy/generate")

    @router.get("/message-strategy/{message_strategy_id}/ugc-creatives/generate")
    def _legacy_get_8(message_strategy_id: str):
        raise HTTPException(status_code=410, detail="This endpoint now requires POST /message-strategy/{message_strategy_id}/ugc-creatives/generate")

    @router.get("/message-strategy/{message_strategy_id}/ad-strategy/generate")
    def _legacy_get_9(message_strategy_id: str):
        raise HTTPException(status_code=410, detail="This endpoint now requires POST /message-strategy/{message_strategy_id}/ad-strategy/generate")

    @router.get("/ad-strategy/{ad_strategy_id}/creative-strategy/generate")
    def _legacy_get_10(ad_strategy_id: str):
        raise HTTPException(status_code=410, detail="This endpoint now requires POST /ad-strategy/{ad_strategy_id}/creative-strategy/generate")

    @router.get("/message-strategy/{message_strategy_id}/page-strategy/generate")
    def _legacy_get_11(message_strategy_id: str):
        raise HTTPException(status_code=410, detail="This endpoint now requires POST /message-strategy/{message_strategy_id}/page-strategy/generate")

    @router.get("/page-requirements/{page_requirements_id}/page-blueprint/generate")
    def _legacy_get_12(page_requirements_id: str):
        raise HTTPException(status_code=410, detail="This endpoint now requires POST /page-requirements/{page_requirements_id}/page-blueprint/generate")

    @router.get("/page-blueprint/{page_blueprint_id}/page-content-plan/generate")
    def _legacy_get_13(page_blueprint_id: str):
        raise HTTPException(status_code=410, detail="This endpoint now requires POST /page-blueprint/{page_blueprint_id}/page-content-plan/generate")

    @router.get("/page-content-plan/{page_content_plan_id}/page-copy/generate")
    def _legacy_get_14(page_content_plan_id: str):
        raise HTTPException(status_code=410, detail="This endpoint now requires POST /page-content-plan/{page_content_plan_id}/page-copy/generate")

    @router.get("/offer-profiles/{offer_profile_id}/analysis/create")
    def _legacy_get_15(offer_profile_id: str):
        raise HTTPException(status_code=410, detail="This endpoint now requires POST /offer-profiles/{offer_profile_id}/analysis/create")

    @router.get("/offer-profiles/{offer_profile_id}/analysis/{analysis_id}/checklists/create")
    def _legacy_get_16(offer_profile_id: str, analysis_id: str):
        raise HTTPException(status_code=410, detail="This endpoint now requires POST /offer-profiles/{offer_profile_id}/analysis/{analysis_id}/checklists/create")

    @router.get("/page-strategy/{page_strategy_id}/page-requirements/create")
    def _legacy_get_17(page_strategy_id: str):
        raise HTTPException(status_code=410, detail="This endpoint now requires POST /page-strategy/{page_strategy_id}/page-requirements/create")

    @router.get("/offers/create")
    def _legacy_get_18():
        raise HTTPException(status_code=410, detail="This endpoint now requires POST /offers/create")

    @router.get("/creative-strategy/{creative_strategy_id}/ad-execution/create")
    def _legacy_get_19(creative_strategy_id: str):
        raise HTTPException(status_code=410, detail="This endpoint now requires POST /creative-strategy/{creative_strategy_id}/ad-execution/create")

    @router.get("/ad-execution/{ad_execution_id}/creative-execution/generate")
    def _legacy_get_20(ad_execution_id: str):
        raise HTTPException(status_code=410, detail="This endpoint now requires POST /ad-execution/{ad_execution_id}/creative-execution/generate")




    # -----------------------------
    # Offers
    # -----------------------------

    @router.get("/offers")
    def offers(page: int = 1):
        return get_offers( page=page )

    # POST in future
    @router.post("/offers/create")
    def create_offer_route(
        name: str,
        description: str | None = None,
    ):
        return create_offer(
            name=name,
            description=description,
        )

    @router.get("/offers/{id}")
    def get_offer_details(id: int):
        return get_offer_handler(id=id)

    @router.post("/offers/{id}/update")
    def update_offer_route(id: int, payload: UpdateFieldsRequest):
        return update_offer_handler(id=id, fields=payload.fields)

    @router.delete("/offers/{id}/delete")
    def delete_offer_route(id: int):
        return delete_offer_handler(id=id)

    @router.get("/offers/{id}/delete")
    def delete_offer_route_legacy_get(id: int):
        raise HTTPException(status_code=410, detail="This endpoint now requires DELETE /offers/{id}/delete")


    # -----------------------------
    # OfferProfiles
    # -----------------------------

    # POST in future
    @router.post("/offers/{id}/offer-profiles/generate")
    def offer_profile_generate(id: int):
        return offer_profile_generate_handler(offer_id=id)

    #  POST in future
    @router.get("/offers/{offer_id}/offer-profiles")
    def get_offer_profiles(offer_id: int):
        return get_offer_profiles_handler(offer_id=offer_id)


    #  POST in future
    @router.get("/offer-profiles/{offer_profile_id}")
    def get_offer_profile( offer_profile_id : int):
        return get_offer_profile_handler( offer_profile_id=offer_profile_id)

    @router.post("/offer-profiles/{id}/update")
    def update_offer_profile_route(id: int, payload: UpdateFieldsRequest):
        return update_offer_profile_handler(id=id, fields=payload.fields)

    # @router.get("/offer-profiles/{offer_profile_id}/suggestions")
    # def suggest_offer_profile_data(offer_profile_id: int):
    #     return suggest_offer_profile_data_handler(offer_profile_id=offer_profile_id)

    @router.delete("/offer-profiles/{id}/delete")
    def delete_offer_profile_route(id: int):
        return delete_offer_profile_handler(id=id)

    @router.get("/offer-profiles/{id}/delete")
    def delete_offer_profile_route_legacy_get(id: int):
        raise HTTPException(status_code=410, detail="This endpoint now requires DELETE /offer-profiles/{id}/delete")

    @router.get("/offer-profiles/{offer_profile_id}/elements")
    def get_offer_profile_elements(offer_profile_id: int):
        return list_offer_profile_elements_handler(offer_profile_id=offer_profile_id)

    @router.get("/offer-profile-elements/types")
    def get_offer_profile_element_types():
        return list_offer_profile_element_types_handler()

    @router.post("/offer-profiles/{offer_profile_id}/elements/generate")
    def generate_offer_profile_elements_route(
        offer_profile_id: int,
        payload: GenerateOfferProfileElementsRequest,
    ):
        return generate_offer_profile_elements_handler(
            offer_profile_id=offer_profile_id,
            element_types=payload.element_types,
            examples_per_type=payload.examples_per_type,
        )

    @router.post("/offer-profiles/{offer_profile_id}/elements")
    def create_offer_profile_element(
        offer_profile_id: int,
        payload: CreateOfferProfileElementRequest,
    ):
        try:
            return create_offer_profile_element_handler(
                offer_profile_id=offer_profile_id,
                element_type=payload.type,
                name=payload.name.strip(),
                description=payload.description.strip() if payload.description else None,
            )
        except LookupError as error:
            raise HTTPException(status_code=404, detail=str(error)) from error

    @router.post("/offer-profile-elements/{id}/update")
    def update_offer_profile_element_route(id: int, payload: UpdateFieldsRequest):
        try:
            return update_offer_profile_element_handler(id=id, fields=payload.fields)
        except LookupError as error:
            raise HTTPException(status_code=404, detail=str(error)) from error

    @router.delete("/offer-profile-elements/{id}/delete")
    def delete_offer_profile_element_route(id: int):
        return delete_offer_profile_element_handler(id=id)

    # -----------------------------
    # Target audience
    # -----------------------------

    #  POST in future
    @router.post("/offer-profiles/{offer_profile_id}/target-audiences/generate")
    def generate_target_audience(offer_profile_id: int):
        return generate_target_audience_handler( offer_profile_id=offer_profile_id)

    # #  GET in future
    @router.get("/offer-profiles/{offer_profile_id}/target-audiences")
    def get_target_audience( offer_profile_id: int):
        return get_target_audience_handler( offer_profile_id=offer_profile_id)

    # #  GET in future
    @router.get("/target-audiences/{target_audience_id}")
    def get_target_audience_preview( target_audience_id: int):
        return get_target_audience_preview_handler( target_audience_id=target_audience_id)

    @router.delete("/target-audiences/{id}/delete")
    def delete_target_audience_route(id: int):
        return delete_target_audience_handler(id=id)

    @router.get("/target-audiences/{id}/delete")
    def delete_target_audience_route_legacy_get(id: int):
        raise HTTPException(status_code=410, detail="This endpoint now requires DELETE /target-audiences/{id}/delete")

    @router.post("/target-audiences/{id}/update")
    def update_target_audience_route(id: int, payload: UpdateTargetAudienceRequest):
        return update_target_audience_handler(
            id=id,
            fields=payload.model_dump(exclude_unset=True, mode="json"),
        )



    # -----------------------------
    # Analysis
    # -----------------------------
    # POST in future
    @router.get("/analysis/{analyse_id}")
    def get_anlysis_by_id(analyse_id: int):
        return get_analysis_by_id_handler( analyse_id=analyse_id)

    @router.post("/offer-profiles/{offer_profile_id}/analysis/create")
    def create_analysis_for_offer_profile(offer_profile_id: int):
        return create_analysis_for_offer_profile_handler(offer_profile_id=offer_profile_id)

    @router.get("/offer-profiles/{offer_profile_id}/analysis")
    def get_analysis_for_offer_profile(offer_profile_id: int):
        return get_analysis_for_offer_profile_handler(offer_profile_id=offer_profile_id)

    # POST in future
    @router.post("/offer-profiles/{offer_profile_id}/analysis/{analyse_id}/answers/generate")
    def offer_profile_analysis_answers_generate(offer_profile_id: int, analyse_id: int):
        return offer_profile_analysis_answers_generate_handler( offer_profile_id=offer_profile_id, analyse_id=analyse_id)

    @router.delete("/analysis/{id}/delete")
    def delete_analysis_route(id: int):
        return delete_analysis_handler(id=id)

    @router.get("/analysis/{id}/delete")
    def delete_analysis_route_legacy_get(id: int):
        raise HTTPException(status_code=410, detail="This endpoint now requires DELETE /analysis/{id}/delete")

    @router.delete("/analysis-questions/{id}/delete")
    def delete_analysis_question_route(id: int):
        return delete_analysis_question_handler(id=id)

    @router.get("/analysis-questions/{id}/delete")
    def delete_analysis_question_route_legacy_get(id: int):
        raise HTTPException(status_code=410, detail="This endpoint now requires DELETE /analysis-questions/{id}/delete")



    # -----------------------------
    # Checklist
    # -----------------------------
    @router.get("/checklists/{checklist_id}")
    def get_checklist_for_analysis( checklist_id: int):
        return get_checklist_by_id_handler( checklist_id=checklist_id)

    @router.delete("/checklists/{id}/delete")
    def delete_checklist_route(id: int):
        return delete_checklist_handler(id=id)

    @router.get("/checklists/{id}/delete")
    def delete_checklist_route_legacy_get(id: int):
        raise HTTPException(status_code=410, detail="This endpoint now requires DELETE /checklists/{id}/delete")

    @router.post("/offer-profiles/{offer_profile_id}/analysis/{analysis_id}/checklists/create")
    def create_analyse_checklist(offer_profile_id: int, analysis_id: int):
        return create_checklist_for_analysis_handler( analysis_id=analysis_id)

    # POST in future
    @router.post("/offer-profiles/{offer_profile_id}/analysis/{analyse_id}/checklists/{checklist_id}/generate")
    def analyse_checklist_generate(offer_profile_id: int, analyse_id: int, checklist_id: int):
        return analyse_checklist_generate_handler( offer_profile_id=offer_profile_id, analyse_id=analyse_id, checklist_id=checklist_id)

    @router.get("/analysis/{analysis_id}/checklists")
    def get_checklist_for_analysis( analysis_id: int):
        return get_analyse_checklists_handler( analyse_id=analysis_id)

    @router.delete("/checklist-items/{id}/delete")
    def delete_checklist_item_route(id: int):
        return delete_checklist_item_handler(id=id)

    @router.get("/checklist-items/{id}/delete")
    def delete_checklist_item_route_legacy_get(id: int):
        raise HTTPException(status_code=410, detail="This endpoint now requires DELETE /checklist-items/{id}/delete")



    # -----------------------------
    # Brand marketing
    # -----------------------------
    @router.post("/offer-profiles/{offer_profile_id}/brand-marketing/generate")
    def offer_profile_brand_marketing_generate( offer_profile_id: int ):
        return generate_brand_marketing_handler( offer_profile_id=offer_profile_id )

    @router.get("/offer-profiles/{offer_profile_id}/brand-marketing")
    def get_offer_profile_brand_marketing( offer_profile_id: int ):
        return get_offer_profile_brand_marketings_handler( offer_profile_id=offer_profile_id )

    @router.get("/brand-marketing/{id}")
    def get_brand_marketing( id: int ):
        return get_brand_marketing_handler( id=id )

    @router.post("/brand-marketing/{id}/update")
    def update_brand_marketing_route(id: int, payload: UpdateFieldsRequest):
        return update_brand_marketing_handler(id=id, fields=payload.fields)

    @router.delete("/brand-marketing/{id}/delete")
    def delete_brand_marketing_route(id: int):
        return delete_brand_marketing_handler(id=id)

    @router.get("/brand-marketing/{id}/delete")
    def delete_brand_marketing_route_legacy_get(id: int):
        raise HTTPException(status_code=410, detail="This endpoint now requires DELETE /brand-marketing/{id}/delete")


    # -----------------------------
    # Marketing strategy
    # -----------------------------
    @router.post("/offer-profiles/{offer_profile_id}/brand-marketing/{brand_markeging_id}/marketing-strategy/generate")
    def offer_profile_marketing_strategy_generate( offer_profile_id: int, brand_markeging_id: int ):
        try:
            return generate_marketing_strategy_handler( offer_profile_id=offer_profile_id, brand_markeging_id=brand_markeging_id )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    @router.get("/brand-marketing/{brand_marketing_id}/marketing-strategy")
    def get_brand_marketing_marketing_strategies( brand_marketing_id: int ):
        return get_brand_marketing_marketing_strategies_handler( brand_marketing_id=brand_marketing_id )

    @router.get("/marketing-strategy/{id}")
    def get_marketing_strategy( id: int ):
        return get_marketing_strategy_handler( id=id )

    @router.post("/marketing-strategy/{id}/update")
    def update_marketing_strategy_route(id: int, payload: UpdateFieldsRequest):
        return update_marketing_strategy_handler(id=id, fields=payload.fields)

    @router.delete("/marketing-strategy/{id}/delete")
    def delete_marketing_strategy_route(id: int):
        return delete_marketing_strategy_handler(id=id)

    @router.get("/marketing-strategy/{id}/delete")
    def delete_marketing_strategy_route_legacy_get(id: int):
        raise HTTPException(status_code=410, detail="This endpoint now requires DELETE /marketing-strategy/{id}/delete")


    # -----------------------------
    # Offer strategy
    # -----------------------------
    @router.post("/marketing-strategy/{marketing_strategy_id}/offer-strategy/generate")
    def offer_profile_offer_strategy_generate(  marketing_strategy_id: int ):
        return generate_offer_strategy_handler(
            marketing_strategy_id=marketing_strategy_id
        )

    @router.get("/marketing-strategy/{marketing_strategy_id}/offer-strategy")
    def get_marketing_strategy_offer_strategies( marketing_strategy_id: int ):
        return get_marketing_strategy_offer_strategies_handler( marketing_strategy_id=marketing_strategy_id )

    @router.get("/offer-strategy/{id}")
    def get_offer_strategy( id: int ):
        return get_offer_strategy_handler( id=id )

    @router.post("/offer-strategy/{id}/update")
    def update_offer_strategy_route(id: int, payload: UpdateFieldsRequest):
        return update_offer_strategy_handler(id=id, fields=payload.fields)

    @router.delete("/offer-strategy/{id}/delete")
    def delete_offer_strategy_route(id: int):
        return delete_offer_strategy_handler(id=id)

    @router.get("/offer-strategy/{id}/delete")
    def delete_offer_strategy_route_legacy_get(id: int):
        raise HTTPException(status_code=410, detail="This endpoint now requires DELETE /offer-strategy/{id}/delete")


    # -----------------------------
    # Message strategy
    # -----------------------------
    @router.post("/offer-strategy/{offer_strategy_id}/message-strategy/generate")
    def offer_profile_message_strategy_generate( offer_strategy_id: int ):
        return generate_message_strategy_handler(
            offer_strategy_id=offer_strategy_id
        )

    @router.get("/offer-strategy/{offer_strategy_id}/message-strategy")
    def get_offer_strategy_message_strategies( offer_strategy_id: int ):
        return get_offer_strategy_message_strategies_handler( offer_strategy_id=offer_strategy_id )

    @router.get("/message-strategy/{id}")
    def get_message_strategy( id: int ):
        return get_message_strategy_handler( id=id )

    @router.post("/message-strategy/{id}/update")
    def update_message_strategy_route(id: int, payload: UpdateFieldsRequest):
        return update_message_strategy_handler(id=id, fields=payload.fields)

    @router.delete("/message-strategy/{id}/delete")
    def delete_message_strategy_route(id: int):
        return delete_message_strategy_handler(id=id)

    @router.get("/message-strategy/{id}/delete")
    def delete_message_strategy_route_legacy_get(id: int):
        raise HTTPException(status_code=410, detail="This endpoint now requires DELETE /message-strategy/{id}/delete")



    # -----------------------------
    # UGC creatives
    # -----------------------------
    @router.post("/message-strategy/{message_strategy_id}/ugc-creatives/generate")
    def offer_profile_ugc_creatives_generate( message_strategy_id: int ):
        return generate_ugc_creatives_handler(
            message_strategy_id=message_strategy_id
        )

    @router.get("/message-strategy/{message_strategy_id}/ugc-creatives")
    def get_message_strategy_ugc_creatives( message_strategy_id: int ):
        return get_message_strategy_ugc_creatives_handler( message_strategy_id=message_strategy_id )

    @router.get("/ugc-creatives/{id}")
    def get_ugc_creative( id: int ):
        return get_ugc_creative_handler( id=id )

    @router.delete("/ugc-creatives/{id}/delete")
    def delete_ugc_creative_route(id: int):
        return delete_ugc_creative_handler(id=id)

    @router.get("/ugc-creatives/{id}/delete")
    def delete_ugc_creative_route_legacy_get(id: int):
        raise HTTPException(status_code=410, detail="This endpoint now requires DELETE /ugc-creatives/{id}/delete")



    # -----------------------------
    # Ad strategy
    # -----------------------------
    @router.post("/message-strategy/{message_strategy_id}/ad-strategy/generate")
    def offer_profile_ad_strategy_generate( message_strategy_id: int ):
        return generate_ad_strategy_handler(
            message_strategy_id=message_strategy_id
        )

    @router.get("/message-strategy/{message_strategy_id}/ad-strategy")
    def get_message_strategy_ad_strategies( message_strategy_id: int ):
        return get_message_strategy_ad_strategies_handler( message_strategy_id=message_strategy_id )

    @router.get("/ad-strategy/{id}")
    def get_ad_strategy( id: int ):
        return get_ad_strategy_handler( id=id )

    @router.post("/ad-strategy/{id}/update")
    def update_ad_strategy_route(id: int, payload: UpdateFieldsRequest):
        return update_ad_strategy_handler(id=id, fields=payload.fields)

    @router.delete("/ad-strategy/{id}/delete")
    def delete_ad_strategy_route(id: int):
        return delete_ad_strategy_handler(id=id)

    @router.get("/ad-strategy/{id}/delete")
    def delete_ad_strategy_route_legacy_get(id: int):
        raise HTTPException(status_code=410, detail="This endpoint now requires DELETE /ad-strategy/{id}/delete")



    # -----------------------------
    # Creative strategy
    # -----------------------------
    @router.post("/ad-strategy/{ad_strategy_id}/creative-strategy/generate")
    def offer_profile_creative_strategy_generate( ad_strategy_id: int ):
        return generate_creative_strategy_handler(
            ad_strategy_id=ad_strategy_id
        )

    @router.get("/ad-strategy/{ad_strategy_id}/creative-strategy")
    def get_ad_strategy_creative_strategies( ad_strategy_id: int ):
        return get_ad_strategy_creative_strategies_handler( ad_strategy_id=ad_strategy_id )

    @router.get("/creative-strategy/{id}")
    def get_creative_strategy( id: int ):
        return get_creative_strategy_handler( id=id )

    @router.post("/creative-strategy/{id}/update")
    def update_creative_strategy_route(id: int, payload: UpdateFieldsRequest):
        return update_creative_strategy_handler(id=id, fields=payload.fields)

    @router.delete("/creative-strategy/{id}/delete")
    def delete_creative_strategy_route(id: int):
        return delete_creative_strategy_handler(id=id)

    @router.get("/creative-strategy/{id}/delete")
    def delete_creative_strategy_route_legacy_get(id: int):
        raise HTTPException(status_code=410, detail="This endpoint now requires DELETE /creative-strategy/{id}/delete")


    # -----------------------------
    # Ad execution
    # -----------------------------
    @router.post("/creative-strategy/{creative_strategy_id}/ad-execution/create")
    def creative_strategy_ad_execution_create(
        creative_strategy_id: int,
        creative_type: str,
        platform: str,
        format: str,
        name: str | None = None
    ):
        return create_ad_execution_handler(
            creative_strategy_id=creative_strategy_id,
            creative_type=creative_type,
            platform=platform,
            format=format,
            name=name
        )

    @router.get("/creative-strategy/{creative_strategy_id}/ad-execution")
    def get_creative_strategy_ad_executions( creative_strategy_id: int ):
        return get_creative_strategy_ad_executions_handler( creative_strategy_id=creative_strategy_id )

    @router.get("/ad-execution/{id}")
    def get_ad_execution( id: int ):
        return get_ad_execution_handler( id=id )

    @router.post("/ad-execution/{id}/update")
    def update_ad_execution_route(id: int, payload: UpdateFieldsRequest):
        return update_ad_execution_handler(id=id, fields=payload.fields)

    @router.delete("/ad-execution/{id}/delete")
    def delete_ad_execution_route(id: int):
        return delete_ad_execution_handler(id=id)

    @router.get("/ad-execution/{id}/delete")
    def delete_ad_execution_route_legacy_get(id: int):
        raise HTTPException(status_code=410, detail="This endpoint now requires DELETE /ad-execution/{id}/delete")


    # -----------------------------
    # Ad frameworks / Creative angels
    # -----------------------------
    @router.get("/ad-frameworks")
    def ad_frameworks_list():
        return list_ad_frameworks_handler()

    @router.get("/creative-angels")
    def creative_angels_list():
        return list_creative_angels_handler()

    @router.get("/execution-styles")
    def execution_styles_list():
        return list_execution_styles_handler()

    @router.get("/platforms")
    def platforms_list():
        return list_platforms_handler()

    @router.get("/fact-statuses")
    def fact_statuses_list():
        return list_fact_statuses_handler()

    @router.get("/review-statuses")
    def review_statuses_list():
        return list_review_statuses_handler()

    @router.get("/page-sections")
    def page_sections_list():
        return list_page_sections_handler()

    # -----------------------------
    # Creative execution
    # -----------------------------
    @router.post("/ad-execution/{ad_execution_id}/creative-execution/generate")
    def ad_execution_creative_execution_generate(
        ad_execution_id: int,
        duration_seconds: int | None = None,
        number_of_slides: int | None = None,
        ad_framework_id: str | None = None,
        creative_angle_id: str | None = None,
        execution_style_id: str | None = None
    ):
        return generate_creative_execution_handler(
            ad_execution_id=ad_execution_id,
            duration_seconds=duration_seconds,
            number_of_slides=number_of_slides,
            ad_framework_id=ad_framework_id,
            creative_angle_id=creative_angle_id,
            execution_style_id=execution_style_id
        )

    @router.get("/ad-execution/{ad_execution_id}/creative-execution")
    def get_ad_execution_creative_executions( ad_execution_id: int ):
        return get_ad_execution_creative_executions_handler( ad_execution_id=ad_execution_id )

    @router.get("/creative-execution/{id}")
    def get_creative_execution( id: int ):
        return get_creative_execution_handler( id=id )

    @router.post("/creative-execution/{id}/update")
    def update_creative_execution_route(id: int, payload: UpdateFieldsRequest):
        return update_creative_execution_handler(id=id, fields=payload.fields)

    @router.delete("/creative-execution/{id}/delete")
    def delete_creative_execution_route(id: int):
        return delete_creative_execution_handler(id=id)

    @router.get("/creative-execution/{id}/delete")
    def delete_creative_execution_route_legacy_get(id: int):
        raise HTTPException(status_code=410, detail="This endpoint now requires DELETE /creative-execution/{id}/delete")


    # -----------------------------
    # Page strategy
    # -----------------------------
    @router.post("/message-strategy/{message_strategy_id}/page-strategy/generate")
    def message_strategy_page_strategy_generate( message_strategy_id: int ):
        return generate_page_strategy_json_handler(
            message_strategy_id=message_strategy_id
        )

    @router.get("/message-strategy/{message_strategy_id}/page-strategy")
    def get_message_strategy_page_strategies( message_strategy_id: int ):
        return get_message_strategy_page_strategies_handler( message_strategy_id=message_strategy_id )

    @router.get("/page-strategy/{id}")
    def get_page_strategy( id: int ):
        return get_page_strategy_handler( id=id )

    @router.post("/page-strategy/{id}/update")
    def update_page_strategy_route(id: int, payload: UpdateFieldsRequest):
        return update_page_strategy_handler(id=id, fields=payload.fields)

    @router.delete("/page-strategy/{id}/delete")
    def delete_page_strategy_route(id: int):
        return delete_page_strategy_handler(id=id)

    @router.get("/page-strategy/{id}/delete")
    def delete_page_strategy_route_legacy_get(id: int):
        raise HTTPException(status_code=410, detail="This endpoint now requires DELETE /page-strategy/{id}/delete")


    # -----------------------------
    # Page requirements
    # -----------------------------
    @router.post("/page-strategy/{page_strategy_id}/page-requirements/create")
    def page_strategy_page_requirements_create( page_strategy_id: int ):
        return create_page_requirements_handler(page_strategy_id=page_strategy_id)

    @router.get("/page-strategy/{page_strategy_id}/page-requirements")
    def get_page_strategy_page_requirements( page_strategy_id: int ):
        return get_page_strategy_page_requirements_handler( page_strategy_id=page_strategy_id )

    @router.get("/page-requirements/{id}")
    def get_page_requirements( id: int ):
        return get_page_requirements_handler( id=id )

    @router.post("/page-requirements/{id}/update")
    def update_page_requirements_route(id: int, payload: UpdatePageRequirementsRequest):
        return update_page_requirements_handler(
            id=id,
            section_requirements=[item.dict() for item in payload.section_requirements],
        )

    @router.delete("/page-requirements/{id}/delete")
    def delete_page_requirements_route(id: int):
        return delete_page_requirements_handler(id=id)

    @router.get("/page-requirements/{id}/delete")
    def delete_page_requirements_route_legacy_get(id: int):
        raise HTTPException(status_code=410, detail="This endpoint now requires DELETE /page-requirements/{id}/delete")


    # -----------------------------
    # Page blueprint
    # -----------------------------
    @router.post("/page-requirements/{page_requirements_id}/page-blueprint/generate")
    def page_requirements_page_blueprint_generate( page_requirements_id: int ):
        return generate_page_blueprint_handler(
            page_requirements_id=page_requirements_id
        )

    @router.get("/page-requirements/{page_requirements_id}/page-blueprint")
    def get_page_requirements_page_blueprints( page_requirements_id: int ):
        return get_page_requirements_page_blueprints_handler( page_requirements_id=page_requirements_id )

    @router.get("/page-blueprint/{id}")
    def get_page_blueprint( id: int ):
        return get_page_blueprint_handler( id=id )

    @router.post("/page-blueprint/{id}/update")
    def update_page_blueprint_route(id: int, payload: UpdateFieldsRequest):
        return update_page_blueprint_handler(id=id, fields=payload.fields)

    @router.delete("/page-blueprint/{id}/delete")
    def delete_page_blueprint_route(id: int):
        return delete_page_blueprint_handler(id=id)

    @router.get("/page-blueprint/{id}/delete")
    def delete_page_blueprint_route_legacy_get(id: int):
        raise HTTPException(status_code=410, detail="This endpoint now requires DELETE /page-blueprint/{id}/delete")


    # -----------------------------
    # Page content plan
    # -----------------------------
    @router.post("/page-blueprint/{page_blueprint_id}/page-content-plan/generate")
    def page_blueprint_page_content_plan_generate( page_blueprint_id: int ):
        return generate_page_content_plan_handler(
            page_blueprint_id=page_blueprint_id
        )

    @router.get("/page-blueprint/{page_blueprint_id}/page-content-plan")
    def get_page_blueprint_page_content_plans( page_blueprint_id: int ):
        return get_page_blueprint_page_content_plans_handler( page_blueprint_id=page_blueprint_id )

    @router.get("/page-content-plan/{id}")
    def get_page_content_plan( id: int ):
        return get_page_content_plan_handler( id=id )

    @router.post("/page-content-plan/{id}/update")
    def update_page_content_plan_route(id: int, payload: UpdateFieldsRequest):
        return update_page_content_plan_handler(id=id, fields=payload.fields)

    @router.delete("/page-content-plan/{id}/delete")
    def delete_page_content_plan_route(id: int):
        return delete_page_content_plan_handler(id=id)

    @router.get("/page-content-plan/{id}/delete")
    def delete_page_content_plan_route_legacy_get(id: int):
        raise HTTPException(status_code=410, detail="This endpoint now requires DELETE /page-content-plan/{id}/delete")


    # -----------------------------
    # Page copy
    # -----------------------------
    @router.post("/page-content-plan/{page_content_plan_id}/page-copy/generate")
    def page_content_plan_page_copy_generate( page_content_plan_id: int ):
        return generate_page_copy_handler(
            page_content_plan_id=page_content_plan_id
        )

    @router.get("/page-content-plan/{page_content_plan_id}/page-copy")
    def get_page_content_plan_page_copies( page_content_plan_id: int ):
        return get_page_content_plan_page_copies_handler( page_content_plan_id=page_content_plan_id )

    @router.get("/page-copy/{id}")
    def get_page_copy( id: int ):
        return get_page_copy_handler( id=id )

    @router.post("/page-copy/{id}/update")
    def update_page_copy_route(id: int, payload: UpdateFieldsRequest):
        return update_page_copy_handler(id=id, fields=payload.fields)

    @router.delete("/page-copy/{id}/delete")
    def delete_page_copy_route(id: int):
        return delete_page_copy_handler(id=id)

    @router.get("/page-copy/{id}/delete")
    def delete_page_copy_route_legacy_get(id: int):
        raise HTTPException(status_code=410, detail="This endpoint now requires DELETE /page-copy/{id}/delete")


    # -----------------------------
    # Settings
    # -----------------------------
    @router.get("/settings/output-prompt")
    def get_output_prompt():
        return get_output_prompt_handler()

    @router.post("/settings/output-prompt")
    def save_output_prompt_route( payload: SaveOutputPromptRequest ):
        return save_output_prompt_handler( content=payload.content )

    @router.get("/settings/ollama")
    def get_ollama_settings_route():
        return get_ollama_settings_handler()

    @router.post("/settings/ollama")
    def save_ollama_settings_route( payload: SaveOllamaSettingsRequest ):
        fields = payload.fields.model_dump(exclude_unset=True, mode="json")
        return save_ollama_settings_handler( fields=fields )

    @router.get("/settings/ollama/models")
    def list_ollama_models_route( url: Optional[str] = None ):
        return list_ollama_models_handler( url=url )


    # -----------------------------
    # Pipeline path
    # -----------------------------
    @router.post("/pipeline/path")
    def get_pipeline_path_route( payload: PipelinePathRequest ):
        try:
            return get_pipeline_path_handler( entity_type=payload.entity_type, entity_id=payload.entity_id )
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))


    # -----------------------------
    # OfferProfiles advertisement
    # -----------------------------
    # @router.get("/offer-profiles/{offer_profile_id}/advertisements/generate")
    # def offer_profile_advertisement_generate( offer_profile_id : int, count: int = 3 ):
    #     return offer_profile_advertisement_generate_handler( offer_profile_id=offer_profile_id, count=count )

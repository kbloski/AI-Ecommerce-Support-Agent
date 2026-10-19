from application.dtos.page_blueprint.page_blueprint_fields import PageBlueprintFields, GeneratePageBlueprintRequest
from typing import Any, Dict, List, Literal, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import AnyHttpUrl, BaseModel, Field
from domain.enums.fact_status import FactStatus

from application.handlers.ads.list_ad_frameworks_handler import list_ad_frameworks_handler
from application.handlers.ads.list_creative_angels_handler import list_creative_angels_handler
from application.handlers.ads.list_execution_styles_handler import list_execution_styles_handler
from application.handlers.ads.list_platforms_handler import list_platforms_handler
from application.handlers.ads.list_fact_statuses_handler import list_fact_statuses_handler
from application.handlers.offers.get_offers import get_offers
from application.handlers.offers.create_offer import create_offer
from application.handlers.offers.get_offer import get_offer_handler
from application.handlers.offers.delete_offer import delete_offer_handler
from application.handlers.offer_sources.generate_offer_source_handler import generate_offer_source_handler
from application.handlers.offer_sources.get_offer_source_handler import get_offer_source_handler
from application.handlers.offer_sources.get_offer_sources_handler import get_offer_sources_handler
from application.handlers.offer_sources.delete_offer_source_handler import delete_offer_source_handler
from application.handlers.offers.update_offer_handler import update_offer_handler
from application.handlers.offer_sources.update_offer_source_handler import update_offer_source_handler
from application.handlers.target_audience.generate_target_audience_handler import generate_target_audience_handler
from application.handlers.target_audience.get_target_audience_handler import get_target_audience_handler
from application.handlers.target_audience.get_target_audience_preview_handler import get_target_audience_preview_handler
from application.handlers.target_audience.delete_target_audience_handler import delete_target_audience_handler
from application.handlers.target_audience.update_target_audience_handler import update_target_audience_handler
# from application.handlers.offers.suggest_offer_source_data_handler import suggest_offer_source_data_handler
from application.handlers.analysis.offer_profile_analysis_answers_generate_handler import offer_profile_analysis_answers_generate_handler
from application.handlers.analysis.create_analysis_for_offer_profile_handler import create_analysis_for_offer_profile_handler
from application.handlers.analysis.get_analysis_by_id_hanlder import get_analysis_by_id_handler
from application.handlers.analysis.get_analysis_for_offer_profile_hanlder import get_analysis_for_offer_profile_handler
from application.handlers.analysis.analyse_checklist_generate_handler import analyse_checklist_generate_handler
from application.handlers.analysis.delete_analysis_handler import delete_analysis_handler
from application.handlers.analysis.delete_analysis_question_handler import delete_analysis_question_handler
from application.handlers.analysis.update_analysis_question_handler import update_analysis_question_handler
from application.handlers.analysis.list_analysis_questions_handler import list_analysis_questions_handler
from application.handlers.checklist.create_checklist_for_offer_profile_handler import create_checklist_for_offer_profile_handler
from application.handlers.checklist.get_offer_profile_checklists_handler import get_offer_profile_checklists_handler
from application.handlers.checklist.get_checklist_by_id_handler import get_checklist_by_id_handler
from application.handlers.checklist.delete_checklist_item_handler import delete_checklist_item_handler
from application.handlers.checklist.delete_checklist_handler import delete_checklist_handler
from application.handlers.checklist.update_checklist_item_handler import update_checklist_item_handler
from application.handlers.advertisement.offer_source_advertisement_generate_handler import offer_source_advertisement_generate_handler
from application.handlers.ugc_creatives.generate_ugc_creatives_handler import generate_ugc_creatives_handler
from application.dtos.ugc_creatives.ugc_generation_fields import GenerateUgcRequest
from application.handlers.ugc_creatives.get_ugc_creative_handler import get_ugc_creative_handler
from application.handlers.ugc_creatives.get_offer_profile_ugc_creatives_handler import get_offer_profile_ugc_creatives_handler
from application.handlers.ugc_creatives.delete_ugc_creative_handler import delete_ugc_creative_handler
from application.handlers.ugc_creatives.update_ugc_creative_handler import update_ugc_creative_handler
from application.handlers.page_blueprint.create_page_blueprint_handler import create_page_blueprint_handler
from application.handlers.page_blueprint.generate_page_blueprint_handler import generate_page_blueprint_handler
from application.handlers.page_blueprint.get_page_blueprint_handler import get_page_blueprint_handler
from application.handlers.page_blueprint.get_offer_profile_page_blueprint_handler import get_offer_profile_page_blueprint_handler
from application.handlers.page_blueprint.update_page_blueprint_handler import update_page_blueprint_handler
from application.handlers.page_blueprint.delete_page_blueprint_handler import delete_page_blueprint_handler
from application.handlers.ads.list_page_sections_handler import list_page_sections_handler
from application.handlers.settings.get_rule_set_handler import get_rule_set_handler
from application.handlers.settings.save_rule_set_handler import save_rule_set_handler
from domain.enums.llm_rule_set import LlmRuleSet
from application.handlers.settings.get_ollama_settings_handler import get_ollama_settings_handler
from application.handlers.settings.save_ollama_settings_handler import save_ollama_settings_handler
from application.handlers.settings.list_ollama_models_handler import list_ollama_models_handler


class SaveRuleSetRequest(BaseModel):
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


class UpdateTargetAudienceRequest(BaseModel):
    fact_status: Optional[FactStatus] = None
    is_reviewed: Optional[bool] = None
    name: Optional[str] = None
    age_min: Optional[int] = None
    age_max: Optional[int] = None
    gender: Optional[str] = None
    lifestyles: Optional[List[Any]] = None
    values: Optional[List[Any]] = None
    pain_points: Optional[List[Any]] = None
    motivations: Optional[List[Any]] = None
    buying_triggers: Optional[List[Any]] = None
    desires: Optional[List[Any]] = None


class GenerateOfferSourceRequest(BaseModel):
    generation_instructions: str = Field(default="", max_length=4000)


class GenerateTargetAudiencesRequest(BaseModel):
    count: int = Field(ge=1, le=10)
    generation_instructions: str = Field(default="", max_length=4000)


def register_general_routes(router: APIRouter):

    # -----------------------------
    # Legacy GET endpoints for routes moved to POST/DELETE above.
    # Kept only to return a clear 410 instead of silently mutating data via GET.
    # -----------------------------
    @router.get("/offers/{id}/offer-sources/generate")
    def _legacy_get_0(id: str):
        raise HTTPException(status_code=410, detail="This endpoint now requires POST /offers/{id}/offer-sources/generate")

    @router.get("/offer-profiles/{offer_profile_id}/analysis/{analyse_id}/answers/generate")
    def _legacy_get_2(offer_profile_id: str, analyse_id: str):
        raise HTTPException(status_code=410, detail="This endpoint now requires POST /offer-profiles/{offer_profile_id}/analysis/{analyse_id}/answers/generate")

    @router.get("/offer-profiles/{offer_profile_id}/analysis/{analyse_id}/checklists/{checklist_id}/generate")
    def _legacy_get_3(offer_profile_id: str, analyse_id: str, checklist_id: str):
        raise HTTPException(status_code=410, detail="This endpoint now requires POST /offer-profiles/{offer_profile_id}/checklists/{checklist_id}/generate")

    @router.get("/offer-profiles/{offer_profile_id}/ugc-creatives/generate")
    def _legacy_get_8(offer_profile_id: str):
        raise HTTPException(status_code=410, detail="This endpoint now requires POST /offer-profiles/{offer_profile_id}/ugc-creatives/generate")



    @router.get("/offer-profiles/{offer_profile_id}/analysis/create")
    def _legacy_get_15(offer_profile_id: str):
        raise HTTPException(status_code=410, detail="This endpoint now requires POST /offer-profiles/{offer_profile_id}/analysis/create")

    @router.get("/offer-profiles/{offer_profile_id}/analysis/{analysis_id}/checklists/create")
    def _legacy_get_16(offer_profile_id: str, analysis_id: str):
        raise HTTPException(status_code=410, detail="This endpoint now requires POST /offer-profiles/{offer_profile_id}/checklists/create")


    @router.get("/offers/create")
    def _legacy_get_18():
        raise HTTPException(status_code=410, detail="This endpoint now requires POST /offers/create")


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
    # OfferSources
    # -----------------------------

    # POST in future
    @router.post("/offers/{id}/offer-sources/generate")
    def generate_offer_source(id: int, payload: GenerateOfferSourceRequest | None = None):
        return generate_offer_source_handler(
            offer_id=id,
            generation_instructions=payload.generation_instructions if payload else "",
        )

    #  POST in future
    @router.get("/offers/{offer_id}/offer-sources")
    def get_offer_sources(offer_id: int):
        return get_offer_sources_handler(offer_id=offer_id)


    #  POST in future
    @router.get("/offer-sources/{offer_source_id}")
    def get_offer_source( offer_source_id : int):
        return get_offer_source_handler( offer_source_id=offer_source_id)

    @router.post("/offer-sources/{id}/update")
    def update_offer_source_route(id: int, payload: UpdateFieldsRequest):
        return update_offer_source_handler(id=id, fields=payload.fields)

    # @router.get("/offer-sources/{offer_source_id}/suggestions")
    # def suggest_offer_source_data(offer_source_id: int):
    #     return suggest_offer_source_data_handler(offer_source_id=offer_source_id)

    @router.delete("/offer-sources/{id}/delete")
    def delete_offer_source_route(id: int):
        return delete_offer_source_handler(id=id)

    @router.get("/offer-sources/{id}/delete")
    def delete_offer_source_route_legacy_get(id: int):
        raise HTTPException(status_code=410, detail="This endpoint now requires DELETE /offer-sources/{id}/delete")


    # -----------------------------
    # Target audience
    # -----------------------------

    #  POST in future
    @router.post("/offer-profiles/{offer_profile_id}/target-audiences/generate")
    def generate_target_audience(offer_profile_id: int, payload: GenerateTargetAudiencesRequest):
        return generate_target_audience_handler(
            offer_profile_id=offer_profile_id,
            count=payload.count,
            generation_instructions=payload.generation_instructions,
        )

    # #  GET in future
    @router.get("/offer-profiles/{offer_profile_id}/target-audiences")
    def get_target_audience(
        offer_profile_id: int,
        page: int = Query(default=1, ge=1),
        page_size: int = Query(default=20, ge=1, le=100),
        is_reviewed: bool | None = None,
        sort: Literal["unreviewed_first", "reviewed_first"] = "unreviewed_first",
    ):
        return get_target_audience_handler(
            offer_profile_id=offer_profile_id,
            page=page,
            page_size=page_size,
            is_reviewed=is_reviewed,
            sort=sort,
        )

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

    @router.post("/analysis-questions/{id}/update")
    def update_analysis_question_route(id: int, payload: UpdateFieldsRequest):
        return update_analysis_question_handler(id=id, fields=payload.fields)

    @router.get("/analysis/{analysis_id}/questions")
    def list_analysis_questions(
        analysis_id: int,
        page: int = Query(default=1, ge=1),
        page_size: int = Query(default=20, ge=1, le=100),
        is_reviewed: bool | None = None,
        sort: Literal["unreviewed_first", "reviewed_first"] = "unreviewed_first",
    ):
        return list_analysis_questions_handler(analysis_id, page, page_size, is_reviewed, sort)

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

    @router.post("/offer-profiles/{offer_profile_id}/checklists/create")
    def create_offer_profile_checklist(offer_profile_id: int):
        return create_checklist_for_offer_profile_handler(offer_profile_id=offer_profile_id)

    # POST in future
    @router.post("/offer-profiles/{offer_profile_id}/checklists/{checklist_id}/generate")
    def offer_profile_checklist_generate(offer_profile_id: int, checklist_id: int):
        return analyse_checklist_generate_handler(offer_profile_id=offer_profile_id, checklist_id=checklist_id)

    @router.get("/offer-profiles/{offer_profile_id}/checklists")
    def get_offer_profile_checklists(offer_profile_id: int):
        return get_offer_profile_checklists_handler(offer_profile_id=offer_profile_id)

    @router.delete("/checklist-items/{id}/delete")
    def delete_checklist_item_route(id: int):
        return delete_checklist_item_handler(id=id)

    @router.post("/checklist-items/{id}/update")
    def update_checklist_item_route(id: int, payload: UpdateFieldsRequest):
        return update_checklist_item_handler(id=id, fields=payload.fields)

    @router.get("/checklist-items/{id}/delete")
    def delete_checklist_item_route_legacy_get(id: int):
        raise HTTPException(status_code=410, detail="This endpoint now requires DELETE /checklist-items/{id}/delete")


    # -----------------------------
    # UGC creatives
    # -----------------------------
    @router.post("/offer-profiles/{offer_profile_id}/ugc-creatives/generate")
    def offer_profile_ugc_creatives_generate(offer_profile_id: int, payload: GenerateUgcRequest | None = None):
        return generate_ugc_creatives_handler(offer_profile_id=offer_profile_id, request=payload)

    @router.get("/offer-profiles/{offer_profile_id}/ugc-creatives")
    def get_offer_profile_ugc_creatives(offer_profile_id: int):
        return get_offer_profile_ugc_creatives_handler(offer_profile_id=offer_profile_id)

    @router.get("/ugc-creatives/{id}")
    def get_ugc_creative( id: int ):
        return get_ugc_creative_handler( id=id )

    @router.post("/ugc-creatives/{id}/update")
    def update_ugc_creative_route(id: int, payload: UpdateFieldsRequest):
        return update_ugc_creative_handler(id=id, fields=payload.fields)

    @router.delete("/ugc-creatives/{id}/delete")
    def delete_ugc_creative_route(id: int):
        return delete_ugc_creative_handler(id=id)

    @router.get("/ugc-creatives/{id}/delete")
    def delete_ugc_creative_route_legacy_get(id: int):
        raise HTTPException(status_code=410, detail="This endpoint now requires DELETE /ugc-creatives/{id}/delete")


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

    @router.get("/page-sections")
    def page_sections_list():
        return list_page_sections_handler()


    # -----------------------------
    # Page blueprints
    # -----------------------------
    @router.post("/offer-profiles/{offer_profile_id}/page-blueprints/create")
    def offer_profile_page_blueprint_create(
        offer_profile_id: int,
        payload: PageBlueprintFields,
    ):
        return create_page_blueprint_handler(
            offer_profile_id=offer_profile_id,
            name=payload.name,
            description=payload.description,
            sections=[item.model_dump() for item in payload.sections],
        )

    @router.post("/offer-profiles/{offer_profile_id}/page-blueprints/generate")
    def offer_profile_page_blueprint_generate(offer_profile_id: int, payload: GeneratePageBlueprintRequest):
        return generate_page_blueprint_handler(offer_profile_id=offer_profile_id, request=payload)

    @router.get("/offer-profiles/{offer_profile_id}/page-blueprints")
    def get_offer_profile_page_blueprint( offer_profile_id: int ):
        return get_offer_profile_page_blueprint_handler( offer_profile_id=offer_profile_id )

    @router.get("/page-blueprints/{id}")
    def get_page_blueprint( id: int ):
        return get_page_blueprint_handler( id=id )

    @router.post("/page-blueprints/{id}/update")
    def update_page_blueprint_route(id: int, payload: PageBlueprintFields):
        return update_page_blueprint_handler(
            id=id,
            name=payload.name,
            description=payload.description,
            sections=[item.model_dump() for item in payload.sections],
        )

    @router.delete("/page-blueprints/{id}/delete")
    def delete_page_blueprint_route(id: int):
        return delete_page_blueprint_handler(id=id)

    @router.get("/page-blueprints/{id}/delete")
    def delete_page_blueprint_route_legacy_get(id: int):
        raise HTTPException(status_code=410, detail="This endpoint now requires DELETE /page-blueprints/{id}/delete")


    # -----------------------------
    # Settings
    # -----------------------------
    @router.get("/settings/rules/{rule_set}")
    def get_rule_set_route(rule_set: LlmRuleSet):
        return get_rule_set_handler(rule_set)

    @router.post("/settings/rules/{rule_set}")
    def save_rule_set_route(rule_set: LlmRuleSet, payload: SaveRuleSetRequest):
        return save_rule_set_handler(rule_set, payload.content)

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
    # OfferSources advertisement
    # -----------------------------
    # @router.get("/offer-sources/{offer_source_id}/advertisements/generate")
    # def offer_source_advertisement_generate( offer_source_id : int, count: int = 3 ):
    #     return offer_source_advertisement_generate_handler( offer_source_id=offer_source_id, count=count )

from dependency_injector import containers, providers
from application.services.offer_source_service import OfferSourceService
from application.services.offer_facts_service import OfferFactsService
from application.services.offer_profile_service import OfferProfileService
from application.services.target_audience_service import TargetAudienceService
from application.services.llm_context_composer import LlmContextComposer
from application.services.marketing_angle_service import MarketingAngleService
from application.services.ad_concept_service import AdConceptService
from application.assemblers.offer_profile_assembler import OfferProfileAssembler
from application.services.ai_service import AiService
from application.services.ollama_service import OllamaService
from application.services.product_service import ProductService
from application.services.offer_service import OfferService
from infrastructure.logging.logger import Logger
from infrastructure.parsers.docx_parser import DocxParser
from infrastructure.repositories.offers_repository import OffersRepository
from infrastructure.services.path_service import PathService
from infrastructure.repositories.ad_frameworks_repository import AdFrameworksRepository
from infrastructure.repositories.creative_angels_repository import CreativeAnglesRepository
from infrastructure.repositories.execution_styles_repository import ExecutionStylesRepository
from infrastructure.repositories.platforms_repository import PlatformsRepository
from infrastructure.repositories.page_sections_repository import PageSectionsRepository
from infrastructure.repositories.color_philosophy_repository import ColorPhilosophyRepository
from infrastructure.repositories.typography_philosophy_repository import TypographyPhilosophyRepository
from application.services.ad_framework_service import AdFrameworkService
from application.services.creative_angle_service import CreativeAngleService
from application.services.execution_style_service import ExecutionStyleService
from application.services.platform_service import PlatformService
from application.services.page_sections_service import PageSectionsService
from infrastructure.parsers.txt_parser import TxtParser
from core.settings import Settings
from infrastructure.database.db import SessionLocal
from application.assemblers.offer_assembler import OfferAssembler
from infrastructure.repositories.offer_source_repository import OfferSourceRepository
from infrastructure.repositories.offer_facts_repository import OfferFactsRepository
from infrastructure.repositories.offer_profiles_repository import OfferProfilesRepository
from infrastructure.repositories.additional_contexts_repository import AdditionalContextsRepository
from infrastructure.repositories.notes_repository import NotesRepository
from application.assemblers.offer_source_assembler import OfferSourceAssembler
from infrastructure.repositories.target_audiences_repository import TargetAudiencesRepository
from infrastructure.repositories.marketing_angles_repository import MarketingAnglesRepository
from infrastructure.repositories.ad_concepts_repository import AdConceptsRepository
from infrastructure.repositories.ad_copies_repository import AdCopiesRepository
from infrastructure.repositories.ad_creative_plans_repository import AdCreativePlansRepository
from infrastructure.repositories.brand_styles_repository import BrandStylesRepository
from application.assemblers.target_audience_assembler import TargetAudienceAssembler
from infrastructure.repositories.analysis_repository import AnalysisRepository
from infrastructure.repositories.offer_profile_analysis_repository import OfferProfileAnalysisRepository
from application.assemblers.analysis_assembler import AnalysisAssembler
from infrastructure.repositories.analysis_questions_repository import AnalysisQuestionsRepository
from infrastructure.repositories.question_answer_repository import QuestionAnswerRepository
from infrastructure.repositories.checklist_repository import ChecklistRepository
from infrastructure.repositories.checklist_items_repository import ChecklistItemsRepository
from application.assemblers.checklist_assembler import ChecklistAssembler
from infrastructure.repositories.brand_marketing_repository import BrandMarketingRepository
from application.assemblers.brand_marketing_assembler import BrandMarketingAssembler
from application.services.brand_marketing_service import BrandMarketingService
from infrastructure.repositories.marketing_strategy_repository import MarketingStrategyRepository
from application.assemblers.marketing_strategy_assembler import MarketingStrategyAssembler
from application.services.marketing_strategy_service import MarketingStrategyService
from infrastructure.repositories.offer_strategy_repository import OfferStrategyRepository
from application.assemblers.offer_strategy_assembler import OfferStrategyAssembler
from application.services.offer_strategy_service import OfferStrategyService
from infrastructure.repositories.message_strategy_repository import MessageStrategyRepository
from application.assemblers.message_strategy_assembler import MessageStrategyAssembler
from application.services.message_strategy_service import MessageStrategyService
from infrastructure.repositories.ad_strategy_repository import AdStrategyRepository
from application.assemblers.ad_strategy_assembler import AdStrategyAssembler
from application.services.ad_strategy_service import AdStrategyService
from infrastructure.repositories.creative_strategy_repository import CreativeStrategyRepository
from application.assemblers.creative_strategy_assembler import CreativeStrategyAssembler
from application.services.creative_strategy_service import CreativeStrategyService
from infrastructure.repositories.ugc_creative_repository import UgcCreativeRepository
from application.assemblers.ugc_creative_assembler import UgcCreativeAssembler
from application.services.ugc_creative_service import UgcCreativeService
from infrastructure.repositories.ad_setup_repository import AdSetupRepository
from application.assemblers.ad_setup_assembler import AdSetupAssembler
from application.services.ad_setup_service import AdSetupService
from infrastructure.repositories.creative_execution_setup_repository import CreativeExecutionSetupRepository
from application.assemblers.creative_execution_setup_assembler import CreativeExecutionSetupAssembler
from application.services.creative_execution_setup_service import CreativeExecutionSetupService
from infrastructure.repositories.generate_ad_repository import GenerateAdRepository
from application.assemblers.generate_ad_assembler import GenerateAdAssembler
from application.services.generate_ad_service import GenerateAdService
from infrastructure.repositories.page_strategy_repository import PageStrategyRepository
from application.assemblers.page_strategy_assembler import PageStrategyAssembler
from application.services.page_strategy_service import PageStrategyService
from infrastructure.repositories.page_requirements_repository import PageRequirementsRepository
from infrastructure.repositories.page_section_requirements_repository import PageSectionRequirementsRepository
from application.assemblers.page_requirements_assembler import PageRequirementsAssembler
from application.services.page_requirements_service import PageRequirementsService
from infrastructure.repositories.page_blueprint_repository import PageBlueprintRepository
from application.assemblers.page_blueprint_assembler import PageBlueprintAssembler
from application.services.page_blueprint_service import PageBlueprintService
from infrastructure.repositories.page_content_plan_repository import PageContentPlanRepository
from application.assemblers.page_content_plan_assembler import PageContentPlanAssembler
from application.services.page_content_plan_service import PageContentPlanService
from infrastructure.repositories.page_copy_repository import PageCopyRepository
from application.assemblers.page_copy_assembler import PageCopyAssembler
from application.services.page_copy_service import PageCopyService
from infrastructure.repositories.app_properties_repository import AppPropertiesRepository
from infrastructure.repositories.ad_copy_structures_repository import AdCopyStructuresRepository

class Container(containers.DeclarativeContainer):
    db = providers.Singleton(
        SessionLocal
    )

    logger = providers.Singleton(
        Logger,
        name="app-logger"
    )

    settings = providers.Singleton(
        Settings
    )

    # --------------------------
    # Parsery
    # --------------------------

    docx_parser = providers.Singleton(
        DocxParser,
        logger=logger
    )

    txt_parser = providers.Singleton(
        TxtParser,
        logger=logger
    )

    # --------------------------
    # Repozytoria
    # --------------------------

    offers_repository =  providers.Singleton(
        OffersRepository,
        logger=logger,
        db=db
    )

    offer_source_repository = providers.Singleton(
        OfferSourceRepository,
        logger=logger,
        db=db
    )

    additional_contexts_repository = providers.Singleton(AdditionalContextsRepository, logger=logger, db=db)
    notes_repository = providers.Singleton(NotesRepository, logger=logger, db=db)

    offer_profiles_repository = providers.Singleton(OfferProfilesRepository, logger=logger, db=db)

    offer_facts_repository = providers.Singleton(OfferFactsRepository, logger=logger, db=db)


    target_audiences_repository = providers.Singleton(
        TargetAudiencesRepository,
        logger=logger,
        db=db
    )

    target_audience_service = providers.Factory(
        TargetAudienceService,
        target_audiences_repository=target_audiences_repository,
    )

    marketing_angles_repository = providers.Singleton(MarketingAnglesRepository, logger=logger, db=db)
    marketing_angle_service = providers.Factory(MarketingAngleService, marketing_angles_repository=marketing_angles_repository)
    ad_concepts_repository = providers.Singleton(AdConceptsRepository, logger=logger, db=db)
    ad_copies_repository = providers.Singleton(AdCopiesRepository, logger=logger, db=db)
    ad_creative_plans_repository = providers.Singleton(AdCreativePlansRepository, logger=logger, db=db)
    brand_styles_repository = providers.Singleton(BrandStylesRepository, logger=logger, db=db)
    ad_concept_service = providers.Factory(AdConceptService, ad_concepts_repository=ad_concepts_repository)

    checklist_repository = providers.Singleton(
        ChecklistRepository,
        logger=logger,
        db=db
    )

    checklist_items_repository = providers.Singleton(
        ChecklistItemsRepository,
        logger=logger,
        db=db
    )

    analysis_repository = providers.Singleton(
        AnalysisRepository,
        logger=logger,
        db=db
    )

    analysis_questions_repository = providers.Singleton(
        AnalysisQuestionsRepository,
        logger=logger,
        db=db
    )

    question_answer_repository = providers.Singleton(
        QuestionAnswerRepository,
        logger=logger,
        db=db
    )

    offer_profile_analysis_repository = providers.Singleton(
        OfferProfileAnalysisRepository,
        logger=logger,
        db=db
    )

    brand_marketing_repository = providers.Singleton(
        BrandMarketingRepository,
        logger=logger,
        db=db
    )

    marketing_strategy_repository = providers.Singleton(
        MarketingStrategyRepository,
        logger=logger,
        db=db
    )

    offer_strategy_repository = providers.Singleton(
        OfferStrategyRepository,
        logger=logger,
        db=db
    )

    message_strategy_repository = providers.Singleton(
        MessageStrategyRepository,
        logger=logger,
        db=db
    )

    ad_strategy_repository = providers.Singleton(
        AdStrategyRepository,
        logger=logger,
        db=db
    )

    creative_strategy_repository = providers.Singleton(
        CreativeStrategyRepository,
        logger=logger,
        db=db
    )

    ugc_creative_repository = providers.Singleton(
        UgcCreativeRepository,
        logger=logger,
        db=db
    )

    ad_setup_repository = providers.Singleton(
        AdSetupRepository,
        logger=logger,
        db=db
    )

    creative_execution_setup_repository = providers.Singleton(
        CreativeExecutionSetupRepository,
        logger=logger,
        db=db
    )

    generate_ad_repository = providers.Singleton(
        GenerateAdRepository,
        logger=logger,
        db=db
    )

    page_strategy_repository = providers.Singleton(
        PageStrategyRepository,
        logger=logger,
        db=db
    )

    page_requirements_repository = providers.Singleton(
        PageRequirementsRepository,
        logger=logger,
        db=db
    )

    page_section_requirements_repository = providers.Singleton(
        PageSectionRequirementsRepository,
        logger=logger,
        db=db
    )

    page_blueprint_repository = providers.Singleton(
        PageBlueprintRepository,
        logger=logger,
        db=db
    )

    page_content_plan_repository = providers.Singleton(
        PageContentPlanRepository,
        logger=logger,
        db=db
    )

    page_copy_repository = providers.Singleton(
        PageCopyRepository,
        logger=logger,
        db=db
    )


    # --------------------------
    # Assemblery
    # --------------------------

    offer_assembler = providers.Singleton(
        OfferAssembler,
        logger=logger,
        offers_repository=offers_repository,
    )

    offer_source_assembler = providers.Singleton(
        OfferSourceAssembler,
        logger=logger,
        offer_source_repository=offer_source_repository,
        offer_facts_repository=offer_facts_repository
    )

    target_audience_assembler =  providers.Singleton(
        TargetAudienceAssembler,
        logger=logger,
    )

    analysis_assembler = providers.Singleton(
        AnalysisAssembler,
        logger=logger,
        analysis_questions_repository=analysis_questions_repository,
        question_answer_repository=question_answer_repository
    )

    checklist_assembler = providers.Singleton(
        ChecklistAssembler,
        logger=logger,
        checklist_items_repository=checklist_items_repository
    )

    brand_marketing_assembler = providers.Singleton(
        BrandMarketingAssembler,
        logger=logger,
    )

    marketing_strategy_assembler = providers.Singleton(
        MarketingStrategyAssembler,
        logger=logger,
    )

    offer_strategy_assembler = providers.Singleton(
        OfferStrategyAssembler,
        logger=logger,
    )

    message_strategy_assembler = providers.Singleton(
        MessageStrategyAssembler,
        logger=logger,
    )

    ad_strategy_assembler = providers.Singleton(
        AdStrategyAssembler,
        logger=logger,
    )

    creative_strategy_assembler = providers.Singleton(
        CreativeStrategyAssembler,
        logger=logger,
    )

    ugc_creative_assembler = providers.Singleton(
        UgcCreativeAssembler,
        logger=logger,
    )

    ad_setup_assembler = providers.Singleton(
        AdSetupAssembler,
        logger=logger,
    )

    generate_ad_assembler = providers.Singleton(
        GenerateAdAssembler,
        logger=logger,
    )

    page_strategy_assembler = providers.Singleton(
        PageStrategyAssembler,
        logger=logger,
    )

    page_requirements_assembler = providers.Singleton(
        PageRequirementsAssembler,
        logger=logger,
        page_section_requirements_repository=page_section_requirements_repository
    )

    page_blueprint_assembler = providers.Singleton(
        PageBlueprintAssembler,
        logger=logger,
    )

    page_content_plan_assembler = providers.Singleton(
        PageContentPlanAssembler,
        logger=logger,
    )

    page_copy_assembler = providers.Singleton(
        PageCopyAssembler,
        logger=logger,
    )
    # --------------------------
    # Serwisy
    # --------------------------

    path_service =  providers.Singleton(
        PathService,
        logger=logger,
    )

    ad_frameworks_repository = providers.Singleton(
        AdFrameworksRepository,
        logger=logger,
        path_service=path_service,
    )

    creative_angels_repository = providers.Singleton(
        CreativeAnglesRepository,
        logger=logger,
        path_service=path_service,
    )

    execution_styles_repository = providers.Singleton(
        ExecutionStylesRepository,
        logger=logger,
        path_service=path_service,
    )

    creative_execution_setup_assembler = providers.Singleton(
        CreativeExecutionSetupAssembler,
        logger=logger,
        ad_frameworks_repository=ad_frameworks_repository,
        creative_angels_repository=creative_angels_repository,
        execution_styles_repository=execution_styles_repository,
    )

    platforms_repository = providers.Singleton(
        PlatformsRepository,
        logger=logger,
        path_service=path_service,
    )

    page_sections_repository = providers.Singleton(
        PageSectionsRepository,
        logger=logger,
        path_service=path_service,
    )

    color_philosophy_repository = providers.Singleton(
        ColorPhilosophyRepository,
        logger=logger,
        path_service=path_service,
    )

    typography_philosophy_repository = providers.Singleton(
        TypographyPhilosophyRepository,
        logger=logger,
        path_service=path_service,
    )

    ad_framework_service = providers.Singleton(
        AdFrameworkService,
        logger=logger,
        ad_frameworks_repository=ad_frameworks_repository,
    )

    creative_angle_service = providers.Singleton(
        CreativeAngleService,
        logger=logger,
        creative_angels_repository=creative_angels_repository,
    )

    execution_style_service = providers.Singleton(
        ExecutionStyleService,
        logger=logger,
        execution_styles_repository=execution_styles_repository,
    )

    platform_service = providers.Singleton(
        PlatformService,
        logger=logger,
        platforms_repository=platforms_repository,
    )

    page_sections_service = providers.Singleton(
        PageSectionsService,
        logger=logger,
        page_sections_repository=page_sections_repository,
        page_section_requirements_repository=page_section_requirements_repository,
    )

    app_properties_repository = providers.Singleton(
        AppPropertiesRepository,
        logger=logger,
        db=db
    )

    ad_copy_structures_repository = providers.Singleton(
        AdCopyStructuresRepository, path_service=path_service,
    )

    ollama_service = providers.Singleton(
        OllamaService,
        logger=logger,
        settings=settings,
        app_properties_repository=app_properties_repository,
    )

    ai_service =  providers.Singleton(
        AiService,
        logger=logger,
        path_service=path_service,
        ollama_service=ollama_service,
    )

    offer_facts_service = providers.Singleton(
        OfferFactsService, offer_facts_repository=offer_facts_repository
    )

    offer_source_service = providers.Singleton(
        OfferSourceService,
        logger=logger,
        docx_parser=docx_parser,
        txt_parser=txt_parser,
        path_service=path_service,
        ai_service=ai_service,
        offer_source_repository=offer_source_repository,
        offer_source_assembler=offer_source_assembler
    )

    product_service = providers.Singleton(
        ProductService,
        logger=logger,
        offers_repository=offers_repository,
        ai_service=ai_service,
        path_service=path_service
    )

    offer_service = providers.Singleton(
        OfferService,
        logger=logger,
        offers_repository=offers_repository,
        offer_assembler=offer_assembler,
    )

    offer_profile_assembler = providers.Singleton(
        OfferProfileAssembler, additional_contexts_repository=additional_contexts_repository
    )

    offer_profile_service = providers.Singleton(
        OfferProfileService, offer_profiles_repository=offer_profiles_repository,
        offer_profile_assembler=offer_profile_assembler
    )

    llm_context_composer = providers.Factory(
        LlmContextComposer,
        offer_profile_service=offer_profile_service,
        target_audience_service=target_audience_service,
        offer_service=offer_service,
        offer_source_service=offer_source_service,
        marketing_angle_service=marketing_angle_service,
        ad_concept_service=ad_concept_service,
        ad_copies_repository=ad_copies_repository,
        ad_creative_plans_repository=ad_creative_plans_repository,
        ugc_creative_repository=ugc_creative_repository,
    )

    brand_marketing_service = providers.Singleton(
        BrandMarketingService,
        logger=logger,
        brand_marketing_repository=brand_marketing_repository,
        brand_marketing_assembler=brand_marketing_assembler
    )

    marketing_strategy_service = providers.Singleton(
        MarketingStrategyService,
        logger=logger,
        marketing_strategy_repository=marketing_strategy_repository,
        marketing_strategy_assembler=marketing_strategy_assembler
    )

    offer_strategy_service = providers.Singleton(
        OfferStrategyService,
        logger=logger,
        offer_strategy_repository=offer_strategy_repository,
        offer_strategy_assembler=offer_strategy_assembler
    )

    message_strategy_service = providers.Singleton(
        MessageStrategyService,
        logger=logger,
        message_strategy_repository=message_strategy_repository,
        message_strategy_assembler=message_strategy_assembler
    )

    ad_strategy_service = providers.Singleton(
        AdStrategyService,
        logger=logger,
        ad_strategy_repository=ad_strategy_repository,
        ad_strategy_assembler=ad_strategy_assembler
    )

    creative_strategy_service = providers.Singleton(
        CreativeStrategyService,
        logger=logger,
        creative_strategy_repository=creative_strategy_repository,
        creative_strategy_assembler=creative_strategy_assembler
    )

    ugc_creative_service = providers.Singleton(
        UgcCreativeService,
        logger=logger,
        ugc_creative_repository=ugc_creative_repository,
        ugc_creative_assembler=ugc_creative_assembler
    )

    ad_setup_service = providers.Singleton(
        AdSetupService,
        logger=logger,
        ad_setup_repository=ad_setup_repository,
        ad_setup_assembler=ad_setup_assembler
    )

    creative_execution_setup_service = providers.Singleton(
        CreativeExecutionSetupService,
        logger=logger,
        creative_execution_setup_repository=creative_execution_setup_repository,
        creative_execution_setup_assembler=creative_execution_setup_assembler
    )

    generate_ad_service = providers.Singleton(
        GenerateAdService,
        logger=logger,
        generate_ad_repository=generate_ad_repository,
        generate_ad_assembler=generate_ad_assembler
    )

    page_strategy_service = providers.Singleton(
        PageStrategyService,
        logger=logger,
        page_strategy_repository=page_strategy_repository,
        page_strategy_assembler=page_strategy_assembler
    )

    page_requirements_service = providers.Singleton(
        PageRequirementsService,
        logger=logger,
        page_requirements_repository=page_requirements_repository,
        page_requirements_assembler=page_requirements_assembler,
        page_sections_service=page_sections_service,
    )

    page_blueprint_service = providers.Singleton(
        PageBlueprintService,
        logger=logger,
        page_blueprint_repository=page_blueprint_repository,
        page_blueprint_assembler=page_blueprint_assembler
    )

    page_content_plan_service = providers.Singleton(
        PageContentPlanService,
        logger=logger,
        page_content_plan_repository=page_content_plan_repository,
        page_content_plan_assembler=page_content_plan_assembler
    )

    page_copy_service = providers.Singleton(
        PageCopyService,
        logger=logger,
        page_copy_repository=page_copy_repository,
        page_copy_assembler=page_copy_assembler
    )

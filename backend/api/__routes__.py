import json

from fastapi import FastAPI, APIRouter, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from api.routes.general_routes import register_general_routes
from core.settings import Settings
from api.routes.offer_facts_routes import router as offer_facts_router
from api.routes.offer_profiles_routes import router as offer_profiles_router
from api.routes.additional_contexts_routes import router as additional_contexts_router
from api.routes.notes_routes import router as notes_router
from api.routes.marketing_angles_routes import router as marketing_angles_router
from api.routes.ad_concepts_routes import router as ad_concepts_router
from api.routes.ad_copy_routes import router as ad_copy_router
from api.routes.ad_creative_plans_routes import router as ad_creative_plans_router
from api.routes.brand_styles_routes import router as brand_styles_router
from api.routes.chat_routes import router as chat_router
from api.routes.resource_context_routes import router as resource_context_router
from application.services.llm_result_validation import LlmGenerationError

# Handlers behind /generate routes parse raw LLM JSON and index into it
# directly; any of these means the model returned data that doesn't match
# the expected shape, which is a 502 (upstream/model contract failure), not
# a 500 (our bug) or a silent 200 with an error body. Registered once here
# instead of a try/except in every route.
LLM_RESPONSE_ERRORS = (json.JSONDecodeError, KeyError, TypeError)

class Routes:

    def __init__(self, app: FastAPI):
        self.app = app
        self.router = APIRouter()

        self._add_middleware()
        self._add_exception_handlers()
        self._add_endpoints()

    def register(self):
        self.app.include_router(self.router)

    # -------------------------
    # MIDDLEWARE
    # -------------------------
    def _add_middleware(self):
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=Settings().get_cors_allowed_origins(),
            allow_credentials=False,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # -------------------------
    # EXCEPTION HANDLERS
    # -------------------------
    def _add_exception_handlers(self):
        @self.app.exception_handler(LlmGenerationError)
        def _handle_llm_generation_error(request: Request, exc: LlmGenerationError):
            return JSONResponse(status_code=502, content={"detail": exc.message})

        def _handle_llm_response_shape_error(request: Request, exc: Exception):
            return JSONResponse(status_code=502, content={"detail": f"LLM response error: {exc}"})

        for exc_type in LLM_RESPONSE_ERRORS:
            self.app.add_exception_handler(exc_type, _handle_llm_response_shape_error)

    # -------------------------
    # ROUTES
    # -------------------------
    def _add_endpoints(self):

        @self.router.get("/")
        def home():
            return {
                "status": "ok",
                "running": True
            }

        register_general_routes( self.router )
        self.router.include_router(offer_facts_router)
        self.router.include_router(offer_profiles_router)
        self.router.include_router(additional_contexts_router)
        self.router.include_router(notes_router)
        self.router.include_router(marketing_angles_router)
        self.router.include_router(ad_concepts_router)
        self.router.include_router(ad_copy_router)
        self.router.include_router(ad_creative_plans_router)
        self.router.include_router(brand_styles_router)
        self.router.include_router(chat_router)
        self.router.include_router(resource_context_router)

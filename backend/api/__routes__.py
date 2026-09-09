import json

from fastapi import FastAPI, APIRouter, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from api.routes.general_routes import register_general_routes
from core.settings import Settings
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
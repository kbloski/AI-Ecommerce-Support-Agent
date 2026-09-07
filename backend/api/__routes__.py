from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from api.routes.general_routes import register_general_routes
from core.settings import Settings

class Routes:

    def __init__(self, app: FastAPI):
        self.app = app
        self.router = APIRouter()

        self._add_middleware()
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
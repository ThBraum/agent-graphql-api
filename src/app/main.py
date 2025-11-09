from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.interface.graphql_schema import get_router


def create_app() -> FastAPI:
    app = FastAPI(title="Agent GraphQL API")

    # CORS
    if settings.allowed_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.allowed_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Health check
    @app.get("/healthz")
    async def healthz():
        return {"status": "ok"}

    # GraphQL
    app.include_router(get_router(), prefix="/graphql")

    return app


app = create_app()

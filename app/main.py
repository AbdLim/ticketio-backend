from typing import AsyncGenerator
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.core.logging import logger, setup_logging
from app.core.config import Settings
from app.db.session import init_db
from app.api.v1 import api_router

settings = Settings()


async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("Starting application...")
    await init_db()
    logger.info("App running...")
    yield
    logger.info("Shutting down application...")


def init_app() -> FastAPI:
    setup_logging()
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        lifespan=lifespan,
        openapi_url=f"/api/v1/openapi.json",
        docs_url="/api/v1/docs",
    )

    # Set up CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    #
    app.include_router(api_router, prefix=settings.API_V1_STR)

    logger.info(f"Application {settings.PROJECT_NAME} v{settings.VERSION} initialized")
    return app


app = init_app()


@app.get("/")
async def root():
    return {
        "message": "Welcome to Fastapify API",
        "docs": "/docs",
        "redoc": "/redoc",
    }


def start():
    uvicorn.run("app.main:app", host="localhost", port=5556, reload=True)

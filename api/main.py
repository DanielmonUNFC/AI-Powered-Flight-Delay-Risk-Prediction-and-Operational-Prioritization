import logging
from contextlib import asynccontextmanager
from typing import Dict, Union

from fastapi import FastAPI, HTTPException

from api.core.config import get_settings
from api.db.databricks import execute_query
from api.routers.explorer import router as explorer_router
from api.routers.overview import router as overview_router
from api.routers.prioritization import router as prioritization_router
from api.services.explorer_service import warm_explorer_cache
from api.services.overview_service import warm_overview_cache
from api.services.prioritization_service import warm_prioritization_cache


logger = logging.getLogger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    """
    Warm Databricks-backed caches when the API starts.

    This moves the first Databricks connection cost to server startup
    instead of the first Streamlit request.
    """
    try:
        warm_overview_cache()
        logger.info("Overview cache warmed at startup.")
    except Exception as error:
        logger.warning("Overview warm-up failed: %s", error)

    try:
        warm_explorer_cache(limit=1000)
        logger.info("Explorer cache warmed at startup (limit=1000).")
    except Exception as error:
        logger.warning("Explorer warm-up failed: %s", error)

    try:
        warm_prioritization_cache()
        logger.info("Prioritization cache warmed at startup (K=25).")
    except Exception as error:
        logger.warning("Prioritization warm-up failed: %s", error)

    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="API for the Flight Delay Risk Prediction capstone project.",
    lifespan=lifespan,
)

app.include_router(
    overview_router,
    prefix=settings.api_prefix,
)
app.include_router(
    explorer_router,
    prefix=settings.api_prefix,
)
app.include_router(
    prioritization_router,
    prefix=settings.api_prefix,
)


@app.get("/")
def root() -> Dict[str, str]:
    """
    Return basic information about the API.
    """
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "documentation": "/docs",
    }


@app.get(f"{settings.api_prefix}/health")
def health_check() -> Dict[str, str]:
    """
    Verify that the FastAPI application is running.
    """
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
    }


@app.get(f"{settings.api_prefix}/health/databricks")
def databricks_health_check() -> Dict[str, Union[str, int]]:
    """
    Verify the connection to Databricks and access to the clean table.
    """
    query = f"""
        SELECT COUNT(*) AS total_records
        FROM {settings.clean_table_full_name}
    """

    try:
        results = execute_query(query)

        return {
            "status": "healthy",
            "table": settings.clean_table_full_name,
            "total_records": results[0]["total_records"],
        }

    except Exception as error:
        raise HTTPException(
            status_code=503,
            detail=f"Databricks connection failed: {error}",
        ) from error

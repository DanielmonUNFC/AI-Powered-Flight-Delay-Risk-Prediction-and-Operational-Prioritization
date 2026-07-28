from typing import Dict, Union

from fastapi import FastAPI, HTTPException

from api.core.config import get_settings
from api.db.databricks import execute_query
from api.routers.overview import router as overview_router


settings = get_settings()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="API for the Flight Delay Risk Prediction capstone project.",
)

app.include_router(
    overview_router,
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
from typing import Any, Dict

from api.core.config import get_settings
from api.db.databricks import execute_query


settings = get_settings()


def get_overview_kpis() -> Dict[str, Any]:
    """
    Calculate the main KPIs displayed on the Overview page.

    Returns:
        A dictionary containing total flights, delay rate,
        average arrival delay, and cancellation rate.
    """
    query = f"""
        SELECT
            COUNT(*) AS total_flights,

            ROUND(
                AVG(
                    CASE
                        WHEN ArrDel15 = 1 THEN 1.0
                        ELSE 0.0
                    END
                ) * 100,
                2
            ) AS delay_rate,

            ROUND(
                AVG(ArrDelay),
                2
            ) AS average_arrival_delay,

            ROUND(
                AVG(
                    CASE
                        WHEN Cancelled = 1 THEN 1.0
                        ELSE 0.0
                    END
                ) * 100,
                2
            ) AS cancellation_rate

        FROM {settings.clean_table_full_name}
    """

    results = execute_query(query)

    if not results:
        return {
            "total_flights": 0,
            "delay_rate": 0.0,
            "average_arrival_delay": 0.0,
            "cancellation_rate": 0.0,
        }

    return results[0]
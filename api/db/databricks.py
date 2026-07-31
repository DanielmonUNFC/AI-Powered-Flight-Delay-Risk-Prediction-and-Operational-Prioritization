from contextlib import contextmanager
from typing import Any, Dict, Iterator, List, Optional

from databricks import sql

from api.core.config import get_settings


@contextmanager
def get_databricks_connection() -> Iterator[Any]:
    """
    Create a connection to the Databricks SQL Warehouse.

    The connection is automatically closed after use.
    """
    settings = get_settings()

    connection = sql.connect(
        server_hostname=settings.databricks_server_hostname,
        http_path=settings.databricks_http_path,
        access_token=settings.databricks_access_token,
    )

    try:
        yield connection
    finally:
        connection.close()


def execute_query(
    query: str,
    parameters: Optional[List[Any]] = None,
) -> List[Dict[str, Any]]:
    """
    Execute a SQL query in Databricks and return the results
    as a list of dictionaries.
    """
    with get_databricks_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query, parameters or [])

            if cursor.description is None:
                return []

            column_names = [
                column[0]
                for column in cursor.description
            ]

            rows = cursor.fetchall()

    return [
        dict(zip(column_names, row))
        for row in rows
    ]
from contextlib import contextmanager
from typing import Any, Dict, Iterator, List, Optional, Sequence, Tuple

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
    return execute_queries([(query, parameters)])[0]


def execute_queries(
    statements: Sequence[Tuple[str, Optional[List[Any]]]],
) -> List[List[Dict[str, Any]]]:
    """Execute multiple read queries through one Databricks connection."""
    if not statements:
        return []

    results: List[List[Dict[str, Any]]] = []
    with get_databricks_connection() as connection:
        with connection.cursor() as cursor:
            for query, parameters in statements:
                cursor.execute(query, parameters or [])
                results.append(_fetch_cursor_rows(cursor))

    return results


def _fetch_cursor_rows(cursor: Any) -> List[Dict[str, Any]]:
    """Convert the active cursor result into dictionaries."""
    if cursor.description is None:
        return []

    column_names = [column[0] for column in cursor.description]
    return [
        dict(zip(column_names, row))
        for row in cursor.fetchall()
    ]

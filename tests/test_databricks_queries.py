"""Tests for shared Databricks query execution."""

from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from api.db import databricks


class FakeCursor:
    def __init__(self) -> None:
        self.description = [("value",)]
        self.executions: list[tuple[str, list]] = []
        self._value = 0

    def __enter__(self) -> "FakeCursor":
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def execute(self, query: str, parameters: list) -> None:
        self.executions.append((query, parameters))
        self._value += 1

    def fetchall(self) -> list[tuple[int]]:
        return [(self._value,)]


class FakeConnection:
    def __init__(self) -> None:
        self.active_cursor = FakeCursor()

    def cursor(self) -> FakeCursor:
        return self.active_cursor


def test_execute_queries_reuses_one_connection(monkeypatch) -> None:
    connection = FakeConnection()
    connection_uses = 0

    @contextmanager
    def fake_connection() -> Iterator[FakeConnection]:
        nonlocal connection_uses
        connection_uses += 1
        yield connection

    monkeypatch.setattr(databricks, "get_databricks_connection", fake_connection)

    results = databricks.execute_queries(
        [("SELECT 1", None), ("SELECT ?", [2])]
    )

    assert connection_uses == 1
    assert results == [[{"value": 1}], [{"value": 2}]]
    assert connection.active_cursor.executions == [
        ("SELECT 1", []),
        ("SELECT ?", [2]),
    ]

import pytest

from api.services.overview_service import _build_kpis, _build_operational_insight


def test_missing_overview_kpi_fails_explicitly():
    with pytest.raises(RuntimeError, match="Missing required KPI metrics"):
        _build_kpis(
            [{"section": "overview_kpi", "metric_name": "total_flights",
              "metric_value": 10, "metric_text": "10", "sort_order": 1}]
        )


def test_missing_overview_insight_cause_fails_explicitly():
    with pytest.raises(RuntimeError, match="Missing required delay causes"):
        _build_operational_insight(
            [{"cause": "Late Aircraft", "percentage": 40.0}]
        )

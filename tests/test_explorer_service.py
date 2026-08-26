from api.services.explorer_service import _build_where


def test_explorer_filters_are_applied_server_side():
    where_sql, parameters = _build_where(
        {"month": 10, "outcome": "Predicted Delayed", "risk_tier": "HIGH",
         "minimum_risk": 0.4, "origin": "LGA"}
    )
    assert "e.Month = ?" in where_sql
    assert "e.predicted_delay = ?" in where_sql
    assert "e.DelayProb >= ?" in where_sql
    assert parameters == [10, "HIGH", "LGA", 1, 0.4]

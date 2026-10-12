import pandas as pd
import pytest

from src.analytics import calculate_rfm, calculate_retention, segment_customers


def test_calculate_rfm():
    data = pd.DataFrame({
        "customer_id": ["A", "A", "B"],
        "transaction_date": ["2025-01-01", "2025-01-10", "2025-01-05"],
        "amount": [10, 20, 50],
    })
    result = calculate_rfm(data, reference_date="2025-01-11")
    a = result.set_index("customer_id").loc["A"]
    assert a["recency_days"] == 1
    assert a["frequency"] == 2
    assert a["monetary"] == 30


def test_rfm_rejects_missing_columns():
    with pytest.raises(ValueError, match="Missing required columns"):
        calculate_rfm(pd.DataFrame({"customer_id": ["A"]}))


def test_rfm_rejects_negative_amounts():
    data = pd.DataFrame({
        "customer_id": ["A"],
        "transaction_date": ["2025-01-01"],
        "amount": [-5],
    })
    with pytest.raises(ValueError, match="negative"):
        calculate_rfm(data)


def test_segment_customers():
    data = pd.DataFrame({
        "customer_id": ["A", "B", "C", "D"],
        "recency_days": [5, 10, 60, 70],
        "frequency": [5, 1, 4, 1],
        "monetary": [500, 20, 300, 10],
    })
    result = segment_customers(data).set_index("customer_id")
    assert result.loc["A", "segment"] == "Loyal"
    assert result.loc["B", "segment"] == "Recent"
    assert result.loc["C", "segment"] == "At Risk"
    assert result.loc["D", "segment"] == "Needs Attention"


def test_segment_rejects_invalid_values():
    data = pd.DataFrame({
        "customer_id": ["A"],
        "recency_days": [-1],
        "frequency": [1],
        "monetary": [10],
    })
    with pytest.raises(ValueError, match="valid ranges"):
        segment_customers(data)


def test_calculate_retention():
    data = pd.DataFrame({
        "customer_id": ["A", "B", "A", "C"],
        "transaction_date": [
            "2025-01-05", "2025-01-10",
            "2025-02-03", "2025-02-12",
        ],
    })
    result = calculate_retention(data)
    assert result.loc[0, "customers"] == 2
    assert result.loc[1, "customers"] == 2
    assert result.loc[1, "retained_customers"] == 1
    assert result.loc[1, "retention_rate"] == 50.0


def test_empty_retention():
    data = pd.DataFrame(columns=["customer_id", "transaction_date"])
    assert calculate_retention(data).empty

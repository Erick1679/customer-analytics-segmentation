import pandas as pd
import pytest

from src.cleaner import clean_transactions, quality_report


def sample_data():
    return pd.DataFrame({
        "transaction_id": ["T001", "T002", "T002", "T003"],
        "customer_id": [" c001 ", "C002", "C002", None],
        "transaction_date": [
            "2026-01-05",
            "2026/02/06",
            "2026/02/06",
            "2026-13-40",
        ],
        "amount": ["1,200", "500", "500", "-10"],
        "channel": ["online", "RETAIL", "RETAIL", "Online"],
        "country": ["KENYA", "uganda", "uganda", "Kenya"],
    })


def test_cleaning_preserves_rows():
    result = clean_transactions(sample_data())
    assert len(result) == 4


def test_standardizes_text_and_amount():
    result = clean_transactions(sample_data())

    assert result.loc[0, "customer_id"] == "C001"
    assert result.loc[0, "channel"] == "Online"
    assert result.loc[0, "country"] == "Kenya"
    assert result.loc[0, "amount"] == 1200


def test_classifies_records():
    result = clean_transactions(sample_data())

    assert result["data_quality_status"].tolist() == [
        "Valid",
        "Valid",
        "Duplicate",
        "Needs Review",
    ]


def test_quality_report():
    result = clean_transactions(sample_data())
    report = quality_report(result)

    assert report["total_rows"] == 4
    assert report["valid_rows"] == 2
    assert report["duplicate_rows"] == 1
    assert report["needs_review_rows"] == 1


def test_missing_columns():
    with pytest.raises(ValueError, match="Missing required columns"):
        clean_transactions(
            pd.DataFrame({"customer_id": ["C001"]})
        )

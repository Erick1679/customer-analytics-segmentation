"""End-to-end tests for the customer analytics pipeline."""

import pandas as pd

from src.main import run_pipeline


def test_complete_pipeline(tmp_path):
    raw_path = tmp_path / "transactions.csv"
    output_dir = tmp_path / "processed"

    sample = pd.DataFrame({
        "transaction_id": [
            "T001", "T002", "T003", "T004",
            "T005", "T005", "T006", "T007",
        ],
        "customer_id": [
            "A", "B", "A", "C",
            "A", "A", "D", "E",
        ],
        "transaction_date": [
            "2026-01-05",
            "2026-01-10",
            "2026-02-01",
            "2026-02-10",
            "2026-03-01",
            "2026-03-01",
            "2026-13-40",
            "2026-03-20",
        ],
        "amount": [
            100, 200, 150, 300,
            50, 50, 70, -10,
        ],
        "channel": ["Online"] * 8,
        "country": ["Kenya"] * 8,
    })

    sample.to_csv(raw_path, index=False)

    result = run_pipeline(
        input_path=raw_path,
        processed_dir=output_dir,
        reference_date="2026-04-01",
    )

    assert result["quality"] == {
        "total_rows": 8,
        "valid_rows": 5,
        "duplicate_rows": 1,
        "needs_review_rows": 2,
    }

    summary = result["summary"]

    assert summary["valid_transactions"] == 5
    assert summary["unique_customers"] == 3
    assert summary["total_revenue"] == 800.0
    assert summary["repeat_customers"] == 1

    assert result["cleaned_path"].is_file()
    assert result["chart_path"].is_file()
    assert result["chart_path"].stat().st_size > 0

    expected_reports = [
        "customer_segments.csv",
        "customer_retention.csv",
        "monthly_revenue.csv",
        "segment_summary.csv",
        "business_summary.csv",
        "data_quality_summary.csv",
    ]

    for filename in expected_reports:
        assert (result["reports_dir"] / filename).is_file()

    monthly = pd.read_csv(
        result["reports_dir"] / "monthly_revenue.csv"
    )

    assert monthly["revenue"].tolist() == [300, 450, 50]

    retention = pd.read_csv(
        result["reports_dir"] / "customer_retention.csv"
    )

    assert retention["retention_rate"].tolist() == [
        0.0, 50.0, 50.0
    ]

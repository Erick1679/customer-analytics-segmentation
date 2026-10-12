"""Run the complete customer analytics and segmentation pipeline."""

import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd

from .analytics import (
    calculate_retention,
    calculate_rfm,
    segment_customers,
)
from .cleaner import load_clean_save, quality_report


DEFAULT_INPUT = Path("data/raw/customer_transactions.csv")
DEFAULT_OUTPUT = Path("data/processed")


def run_pipeline(
    input_path=DEFAULT_INPUT,
    processed_dir=DEFAULT_OUTPUT,
    reference_date=None,
):
    """Clean transactions, analyze customers, and export reports."""

    processed_dir = Path(processed_dir)
    reports_dir = processed_dir / "reports"
    charts_dir = processed_dir / "charts"

    reports_dir.mkdir(parents=True, exist_ok=True)
    charts_dir.mkdir(parents=True, exist_ok=True)

    # Clean all raw records without silently deleting any.
    cleaned_path = processed_dir / "clean_customer_transactions.csv"

    cleaned = load_clean_save(input_path, cleaned_path)
    quality = quality_report(cleaned)

    # Only valid transactions contribute to business metrics.
    valid = cleaned.loc[
        cleaned["data_quality_status"] == "Valid"
    ].copy()

    if valid.empty:
        raise ValueError("No valid transactions available for analysis")

    reference = (
        pd.Timestamp(reference_date)
        if reference_date is not None
        else valid["transaction_date"].max() + pd.Timedelta(days=1)
    )

    # Customer RFM and segmentation.
    rfm = calculate_rfm(valid, reference_date=reference)
    segments = segment_customers(rfm)

    # Monthly returning-customer retention.
    retention = calculate_retention(valid)

    # Monthly revenue performance.
    monthly_data = valid.copy()
    monthly_data["month"] = (
        monthly_data["transaction_date"].dt.to_period("M").astype(str)
    )

    monthly_revenue = (
        monthly_data.groupby("month", as_index=False)
        .agg(
            transactions=("transaction_id", "count"),
            customers=("customer_id", "nunique"),
            revenue=("amount", "sum"),
        )
        .sort_values("month")
    )

    # Performance by customer segment.
    segment_summary = (
        segments.groupby("segment", as_index=False)
        .agg(
            customers=("customer_id", "count"),
            revenue=("monetary", "sum"),
            average_customer_value=("monetary", "mean"),
        )
        .sort_values("revenue", ascending=False)
    )

    # Business performance indicators.
    total_revenue = float(valid["amount"].sum())
    customer_count = int(valid["customer_id"].nunique())
    transaction_count = len(valid)

    repeat_customers = int((rfm["frequency"] > 1).sum())

    top_three_revenue = float(
        rfm.nlargest(3, "monetary")["monetary"].sum()
    )

    summary = {
        "reference_date": reference.strftime("%Y-%m-%d"),
        "valid_transactions": transaction_count,
        "unique_customers": customer_count,
        "total_revenue": round(total_revenue, 2),
        "average_order_value": round(
            total_revenue / transaction_count, 2
        ),
        "repeat_customers": repeat_customers,
        "repeat_customer_rate_percent": round(
            repeat_customers / customer_count * 100, 2
        ),
        "top_3_revenue_share_percent": round(
            top_three_revenue / total_revenue * 100, 2
        ),
    }

    # Export all CSV reports.
    reports = {
        "customer_segments.csv": segments,
        "customer_retention.csv": retention,
        "monthly_revenue.csv": monthly_revenue,
        "segment_summary.csv": segment_summary,
        "business_summary.csv": pd.DataFrame(
            list(summary.items()),
            columns=["metric", "value"],
        ),
        "data_quality_summary.csv": pd.DataFrame(
            list(quality.items()),
            columns=["metric", "value"],
        ),
    }

    for filename, dataframe in reports.items():
        dataframe.to_csv(reports_dir / filename, index=False)

    # Create and save a revenue chart.
    fig, ax = plt.subplots(figsize=(9, 5))

    ax.bar(
        monthly_revenue["month"],
        monthly_revenue["revenue"],
    )

    ax.set_title("Monthly Customer Revenue")
    ax.set_xlabel("Month")
    ax.set_ylabel("Revenue")
    ax.grid(axis="y", alpha=0.25)

    fig.tight_layout()

    chart_path = charts_dir / "monthly_revenue.png"
    fig.savefig(chart_path, dpi=150)
    plt.close(fig)

    return {
        "quality": quality,
        "summary": summary,
        "segments": segments,
        "retention": retention,
        "reports_dir": reports_dir,
        "chart_path": chart_path,
        "cleaned_path": cleaned_path,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Customer Analytics and Segmentation"
    )

    parser.add_argument(
        "--file",
        default=str(DEFAULT_INPUT),
        help="Path to raw transaction CSV",
    )

    parser.add_argument(
        "--reference-date",
        default=None,
        help="RFM reference date, e.g. 2026-04-30",
    )

    args = parser.parse_args()

    result = run_pipeline(
        input_path=args.file,
        reference_date=args.reference_date,
    )

    print("\nCUSTOMER ANALYTICS AND SEGMENTATION")
    print("=" * 42)

    print("\nDATA QUALITY")
    for name, value in result["quality"].items():
        print(f"{name}: {value}")

    print("\nBUSINESS SUMMARY")
    for name, value in result["summary"].items():
        print(f"{name}: {value}")

    print("\nCUSTOMER SEGMENTS")
    print(
        result["segments"]["segment"]
        .value_counts()
        .to_string()
    )

    print("\nMONTHLY RETENTION")
    print(result["retention"].to_string(index=False))

    print("\nFILES EXPORTED")
    print(f"Cleaned data: {result['cleaned_path']}")
    print(f"CSV reports: {result['reports_dir']}")
    print(f"Revenue chart: {result['chart_path']}")


if __name__ == "__main__":
    main()

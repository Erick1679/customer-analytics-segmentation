"""Clean customer transaction data while preserving quality issues."""

from pathlib import Path

import pandas as pd


REQUIRED_COLUMNS = {
    "transaction_id",
    "customer_id",
    "transaction_date",
    "amount",
    "channel",
    "country",
}


def clean_transactions(df: pd.DataFrame) -> pd.DataFrame:
    """Standardize transactions and classify data quality."""

    missing = REQUIRED_COLUMNS - set(df.columns)

    if missing:
        raise ValueError(
            f"Missing required columns: {sorted(missing)}"
        )

    cleaned = df.copy()

    text_columns = [
        "transaction_id",
        "customer_id",
        "channel",
        "country",
    ]

    for column in text_columns:
        cleaned[column] = (
            cleaned[column]
            .astype("string")
            .str.strip()
            .replace("", pd.NA)
        )

    cleaned["transaction_id"] = (
        cleaned["transaction_id"].str.upper()
    )

    cleaned["customer_id"] = (
        cleaned["customer_id"].str.upper()
    )

    cleaned["channel"] = (
        cleaned["channel"].str.title()
    )

    cleaned["country"] = (
        cleaned["country"].str.title()
    )

    cleaned["transaction_date"] = pd.to_datetime(
        cleaned["transaction_date"],
        format="mixed",
        errors="coerce",
    )

    amount_text = (
        cleaned["amount"]
        .astype("string")
        .str.replace(r"[$,]", "", regex=True)
        .str.strip()
    )

    cleaned["amount"] = pd.to_numeric(
        amount_text,
        errors="coerce",
    )

    duplicates = (
        cleaned["transaction_id"].duplicated(keep="first")
        & cleaned["transaction_id"].notna()
    )

    statuses = []
    issues = []

    for position, (_, row) in enumerate(cleaned.iterrows()):
        problems = []

        if pd.isna(row["transaction_id"]):
            problems.append("Missing transaction ID")

        if pd.isna(row["customer_id"]):
            problems.append("Missing customer ID")

        if pd.isna(row["transaction_date"]):
            problems.append("Invalid or missing date")

        if pd.isna(row["amount"]):
            problems.append("Invalid or missing amount")
        elif row["amount"] <= 0:
            problems.append("Non-positive amount")

        if duplicates.iloc[position]:
            statuses.append("Duplicate")
            problems.append("Duplicate transaction ID")
        elif problems:
            statuses.append("Needs Review")
        else:
            statuses.append("Valid")

        issues.append("; ".join(problems))

    cleaned["data_quality_status"] = statuses
    cleaned["data_quality_issue"] = issues

    return cleaned


def quality_report(df: pd.DataFrame) -> dict:
    """Summarize data-quality classification."""

    counts = df["data_quality_status"].value_counts()

    return {
        "total_rows": len(df),
        "valid_rows": int(counts.get("Valid", 0)),
        "duplicate_rows": int(counts.get("Duplicate", 0)),
        "needs_review_rows": int(counts.get("Needs Review", 0)),
    }


def load_clean_save(
    input_path: str | Path,
    output_path: str | Path,
) -> pd.DataFrame:
    """Load raw transactions, clean them, and save the results."""

    raw = pd.read_csv(input_path, dtype="string")

    cleaned = clean_transactions(raw)

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    cleaned.to_csv(output, index=False)

    return cleaned

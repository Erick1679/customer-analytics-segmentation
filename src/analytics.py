"""Customer segmentation and retention analytics."""

import pandas as pd


def calculate_rfm(
    transactions: pd.DataFrame,
    reference_date: str | pd.Timestamp | None = None,
) -> pd.DataFrame:
    """Calculate recency, frequency, and monetary value per customer."""
    required = {"customer_id", "transaction_date", "amount"}
    missing = required - set(transactions.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    if transactions.empty:
        return pd.DataFrame(
            columns=[
                "customer_id",
                "recency_days",
                "frequency",
                "monetary",
            ]
        )

    data = transactions.copy()
    data["transaction_date"] = pd.to_datetime(
        data["transaction_date"], errors="raise"
    )
    data["amount"] = pd.to_numeric(data["amount"], errors="raise")

    if data[["customer_id", "transaction_date", "amount"]].isna().any().any():
        raise ValueError("Required fields cannot contain missing values")
    if (data["amount"] < 0).any():
        raise ValueError("Transaction amounts cannot be negative")

    reference = (
        pd.Timestamp(reference_date)
        if reference_date is not None
        else data["transaction_date"].max() + pd.Timedelta(days=1)
    )

    if reference.tz is not None:
        reference = reference.tz_localize(None)

    if (data["transaction_date"] > reference).any():
        raise ValueError("Transactions cannot occur after the reference date")

    result = (
        data.groupby("customer_id")
        .agg(
            last_purchase=("transaction_date", "max"),
            frequency=("transaction_date", "size"),
            monetary=("amount", "sum"),
        )
        .reset_index()
    )
    result["recency_days"] = (
        reference.normalize() - result["last_purchase"].dt.normalize()
    ).dt.days

    return result[
        ["customer_id", "recency_days", "frequency", "monetary"]
    ].sort_values("customer_id").reset_index(drop=True)


def segment_customers(rfm: pd.DataFrame) -> pd.DataFrame:
    """Assign simple customer segments using RFM values."""
    required = {"customer_id", "recency_days", "frequency", "monetary"}
    missing = required - set(rfm.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    result = rfm.copy()

    if result.empty:
        result["segment"] = pd.Series(dtype="object")
        return result

    if result[["recency_days", "frequency", "monetary"]].isna().any().any():
        raise ValueError("RFM values cannot contain missing values")
    if (
        (result["recency_days"] < 0).any()
        or (result["frequency"] < 1).any()
        or (result["monetary"] < 0).any()
    ):
        raise ValueError("RFM values are outside valid ranges")

    result["segment"] = "Needs Attention"
    loyal = (result["frequency"] >= 3) & (result["recency_days"] <= 30)
    result.loc[loyal, "segment"] = "Loyal"
    recent = (result["recency_days"] <= 30) & ~loyal
    result.loc[recent, "segment"] = "Recent"
    at_risk = (result["recency_days"] > 30) & (
        result["frequency"] >= 3
    )
    result.loc[at_risk, "segment"] = "At Risk"

    return result


def calculate_retention(
    transactions: pd.DataFrame,
) -> pd.DataFrame:
    """Calculate monthly returning-customer retention.

    Retention for a month is the percentage of customers active in the
    previous month who are also active in the current month.
    """
    required = {"customer_id", "transaction_date"}
    missing = required - set(transactions.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    if transactions.empty:
        return pd.DataFrame(
            columns=["month", "customers", "retained_customers", "retention_rate"]
        )

    data = transactions.copy()
    data["transaction_date"] = pd.to_datetime(
        data["transaction_date"], errors="raise"
    )
    if data[["customer_id", "transaction_date"]].isna().any().any():
        raise ValueError("Customer IDs and transaction dates cannot be missing")

    data["month"] = data["transaction_date"].dt.to_period("M")
    active = data.groupby("month")["customer_id"].apply(set).sort_index()

    rows = []
    previous_customers = None

    for month, customers in active.items():
        retained = (
            len(previous_customers & customers)
            if previous_customers is not None
            else 0
        )
        rate = (
            retained / len(previous_customers) * 100
            if previous_customers
            else 0.0
        )
        rows.append(
            {
                "month": str(month),
                "customers": len(customers),
                "retained_customers": retained,
                "retention_rate": round(rate, 2),
            }
        )
        previous_customers = customers

    return pd.DataFrame(rows)

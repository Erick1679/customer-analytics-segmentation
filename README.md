# Customer Analytics and Segmentation

A Python data analytics project that cleans customer
transaction data, segments customers, measures retention,
and generates business reports and visualizations.

## Project Objectives

- Identify valuable and loyal customers.
- Analyze customer purchasing behavior.
- Measure monthly customer retention.
- Calculate revenue and repeat-purchase metrics.
- Identify and flag data-quality problems.
- Export business reports and a revenue chart.

## Technologies

- Python 3.13
- pandas
- NumPy
- Matplotlib
- pytest

## Features

### Data Cleaning

The cleaning pipeline standardizes transaction data,
converts dates and amounts, detects duplicate transaction
IDs, and flags missing or invalid required values.

Records receive one of three classifications:

- Valid
- Duplicate
- Needs Review

All original records are preserved in the cleaned output.
Only valid records are used for business analysis.

### RFM Customer Segmentation

RFM means:

- Recency: days since the customer's last purchase.
- Frequency: number of purchases.
- Monetary: total customer spending.

The project assigns customers to four segments:

- Loyal
- Recent
- At Risk
- Needs Attention

### Customer Retention

The project calculates monthly returning-customer retention
based on customers active in the previous observed month.

### Business Analytics

The pipeline calculates:

- Total revenue
- Average order value
- Unique customers
- Repeat-customer rate
- Revenue concentration among the top three customers
- Monthly revenue trends

## Running the Project

Create and activate a virtual environment:

    python3 -m venv .venv
    source .venv/bin/activate

Install dependencies:

    python -m pip install pandas numpy matplotlib pytest

Run the complete analysis:

    python -m src.main

Specify a reference date if required:

    python -m src.main --reference-date 2026-04-30

Run automated tests:

    python -m pytest -q

## Dataset

The sample dataset is synthetic and is located at:

    data/raw/customer_transactions.csv

It contains 31 transaction records, including intentionally
messy records for data-quality testing.

## Sample Results

Using the included dataset:

| Metric | Result |
|---|---:|
| Total records | 31 |
| Valid transactions | 26 |
| Duplicate transactions | 1 |
| Records needing review | 4 |
| Unique valid customers | 10 |
| Total revenue | 25,180 |
| Average order value | 968.46 |
| Repeat-customer rate | 70% |
| Top-three customer revenue share | 52.86% |

Customer segmentation:

| Segment | Customers |
|---|---:|
| Loyal | 5 |
| Recent | 4 |
| Needs Attention | 1 |
| At Risk | 0 |

## Generated Outputs

The cleaned dataset is saved to:

    data/processed/clean_customer_transactions.csv

Six CSV reports are saved to:

    data/processed/reports/

The monthly revenue chart is saved to:

    data/processed/charts/monthly_revenue.png

## Project Structure

    customer-analytics-segmentation/
    ├── data/
    │   ├── raw/
    │   └── processed/
    │       ├── reports/
    │       └── charts/
    ├── src/
    │   ├── cleaner.py
    │   ├── analytics.py
    │   └── main.py
    ├── tests/
    │   ├── test_cleaner.py
    │   ├── test_analytics.py
    │   └── test_pipeline.py
    ├── README.md
    └── .gitignore

## Testing

The project includes automated tests for data cleaning,
RFM calculations, customer segmentation, retention, and
the complete reporting pipeline.

## Author

Erick Machogu

## Disclaimer

All sample customer data is synthetic and is provided
for educational and portfolio demonstration purposes.

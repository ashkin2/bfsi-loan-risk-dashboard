# BFSI Loan & Claims Risk Analytics Dashboard

An end-to-end data analytics project simulating a real-world BFSI (Banking & Financial Services) use case: consolidating loan, risk, collections, and insurance-claims data into a single analytics layer and an interactive executive dashboard.

**Live dashboard:** open [`dashboard/index.html`](https://ashkin2.github.io/bfsi-loan-risk-dashboard/dashboard/index.html) in any browser — no server required.

---

## Business Problem

A BFSI operations team needs a single view across its loan portfolio to answer:

- Which regions and loan products carry the most default risk?
- Is our risk-scoring model actually predictive of real defaults?
- How does collections efficiency degrade as accounts age past due?
- Which acquisition channel brings in the healthiest accounts?
- How well is the claims team processing insurance-linked claims?

This project builds the pipeline and dashboard to answer exactly those questions.

---

## Tech Stack

| Layer | Tools |
|---|---|
| Data Generation | Python (NumPy, Pandas) |
| ETL | Python, Pandas (extract → clean → transform) |
| Data Warehouse | SQLite |
| Analysis | SQL (window functions, CASE-based segmentation, aggregations) |
| Dashboard | HTML, CSS, Chart.js (interactive, responsive) |

---

## Project Structure

```
bfsi-project/
├── scripts/
│   ├── generate_data.py         # Generates synthetic BFSI account dataset (6,000 records)
│   └── build_dashboard_data.py  # Runs SQL queries, exports results as dashboard JSON
├── etl/
│   └── etl_pipeline.py          # Extract → Transform → Load into SQLite warehouse
├── sql/
│   └── analysis_queries.sql     # 6 analysis queries: risk, collections, claims, channel, trend
├── data/
│   ├── raw_bfsi_accounts.csv    # Raw generated data
│   └── bfsi.db                  # SQLite warehouse (output of ETL)
├── dashboard/
│   ├── index.html               # Interactive dashboard (open directly in browser)
│   └── dashboard_data.json      # Pre-aggregated data powering the dashboard
├── requirements.txt
└── README.md
```

---

## How to Run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Generate the synthetic dataset
python scripts/generate_data.py

# 3. Run the ETL pipeline (loads data into SQLite)
python etl/etl_pipeline.py

# 4. Build the dashboard's data file by running the SQL analysis layer
python scripts/build_dashboard_data.py

# 5. Open the dashboard
open dashboard/index.html      # macOS
start dashboard/index.html     # Windows
```

To explore the SQL layer directly:

```bash
sqlite3 data/bfsi.db
.read sql/analysis_queries.sql
```

---

## Key Insights (from the generated dataset)

- **Risk model validation:** Default rate rises from ~4.7% in the "Low Risk" tier to ~26.5% in "Critical Risk" — confirming the risk-scoring logic tracks real-world default behavior.
- **Collections decay:** Collection rate on defaulted accounts drops from ~79% (not yet overdue) to ~50% once an account crosses 90 days past due — highlighting the value of early intervention.
- **Channel quality:** Branch and Digital App originations show the lowest default rates (~11.7%), while Call Center-originated accounts run highest (~14.2%) — a signal for acquisition strategy.
- **Claims turnaround:** Approved and Rejected claims are both resolved in ~8.5 days on average, with roughly 52% of claims ultimately approved.

---

## What This Project Demonstrates

- **SQL:** Multi-table-style aggregation, `CASE`-based segmentation/bucketing, window-style ratio calculations
- **Python / ETL:** A clean Extract → Transform → Load pipeline with explicit data-quality checks
- **Data Visualization & Dashboarding:** A multi-chart executive dashboard (KPI cards, trend lines, dual-axis charts, breakdowns) built for stakeholder consumption
- **Business framing:** Every metric ties back to a decision a BFSI risk/collections team would actually make

---

## Note on Data

The dataset is **synthetically generated** (`scripts/generate_data.py`) to resemble realistic BFSI portfolio patterns — no real customer or institutional data is used. This mirrors how analysts often build and demo portfolio work before being granted production data access.

---

**Author:** Ashish Gantait — Senior Data Analyst | Power BI, SQL, Python, ETL
[LinkedIn](https://linkedin.com/in/ashishgantait) · [GitHub](https://github.com/ashkin2)

"""
etl_pipeline.py
----------------
ETL pipeline for the BFSI Loan & Claims Analytics project.

Extract : reads raw synthetic account data (data/raw_bfsi_accounts.csv)
Transform: cleans nulls, derives risk tiers / DPD buckets, validates types
Load    : writes cleaned data into a SQLite warehouse table (data/bfsi.db)
          so the project's SQL layer (sql/analysis_queries.sql) can run
          against it exactly like a real analytics data mart.

Run:  python etl/etl_pipeline.py
"""

import sqlite3
import pandas as pd
from pathlib import Path

RAW_PATH = Path("data/raw_bfsi_accounts.csv")
DB_PATH = Path("data/bfsi.db")


def extract(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    print(f"[EXTRACT] Loaded {len(df)} rows from {path}")
    return df


def transform(df: pd.DataFrame) -> pd.DataFrame:
    before = len(df)

    # --- Data cleaning ---
    df["disbursement_date"] = pd.to_datetime(df["disbursement_date"])
    df["collected_flag"] = df["collected_flag"].fillna(0).astype(int)
    df["claim_status"] = df["claim_status"].fillna("No Claim")
    df["claim_resolution_days"] = df["claim_resolution_days"].fillna(0)

    # Drop any impossible values (defensive data-quality check)
    df = df[(df["credit_score"].between(300, 900)) & (df["loan_amount"] > 0)]

    # --- Derived / transformed columns (business logic layer) ---
    df["risk_tier"] = pd.cut(
        df["risk_score"],
        bins=[-0.01, 0.25, 0.50, 0.75, 1.01],
        labels=["Low Risk", "Medium Risk", "High Risk", "Critical Risk"],
    )

    df["dpd_bucket"] = pd.cut(
        df["days_past_due"],
        bins=[-1, 0, 30, 60, 90, 10000],
        labels=["Not Overdue", "1-30 Days", "31-60 Days", "61-90 Days", "90+ Days"],
    )

    after = len(df)
    print(f"[TRANSFORM] Cleaned data: {before} -> {after} rows "
          f"({before - after} dropped on data-quality checks)")
    return df


def load(df: pd.DataFrame, db_path: Path):
    conn = sqlite3.connect(db_path)
    df.to_sql("accounts", conn, if_exists="replace", index=False)
    conn.commit()
    conn.close()
    print(f"[LOAD] Wrote {len(df)} rows to SQLite warehouse -> {db_path}")


def main():
    df_raw = extract(RAW_PATH)
    df_clean = transform(df_raw)
    load(df_clean, DB_PATH)
    print("[DONE] ETL pipeline completed successfully.")


if __name__ == "__main__":
    main()

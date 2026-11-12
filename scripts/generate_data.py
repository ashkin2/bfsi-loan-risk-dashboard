"""
generate_data.py
-----------------
Generates a realistic synthetic BFSI (Banking/Financial Services) dataset
simulating loan accounts, claims, and risk attributes — used as the raw
input for the ETL pipeline and analytics dashboard.

This mirrors a real-world scenario: a BFSI operations team needs loan
and claims data consolidated for risk scoring, collections efficiency
tracking, and regional performance reporting.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta

np.random.seed(42)

N = 6000

regions = ["North", "South", "East", "West", "Central"]
region_weights = [0.26, 0.22, 0.18, 0.20, 0.14]

loan_types = ["Personal Loan", "Auto Loan", "Home Loan", "Credit Card", "Business Loan"]
loan_type_weights = [0.32, 0.22, 0.18, 0.20, 0.08]

channels = ["Branch", "Digital App", "Call Center", "DSA Partner"]
channel_weights = [0.30, 0.35, 0.15, 0.20]

start_date = datetime(2024, 1, 1)
end_date = datetime(2025, 11, 1)
date_range_days = (end_date - start_date).days

records = []
for i in range(N):
    region = np.random.choice(regions, p=region_weights)
    loan_type = np.random.choice(loan_types, p=loan_type_weights)
    channel = np.random.choice(channels, p=channel_weights)

    disb_date = start_date + timedelta(days=int(np.random.uniform(0, date_range_days)))

    # Loan amount varies by type
    base_amt = {
        "Personal Loan": 250000, "Auto Loan": 600000, "Home Loan": 3200000,
        "Credit Card": 80000, "Business Loan": 1500000
    }[loan_type]
    loan_amount = max(10000, np.random.lognormal(mean=np.log(base_amt), sigma=0.45))

    tenure_months = int(np.random.choice([12, 24, 36, 48, 60, 84, 120, 180],
                                          p=[0.12, 0.18, 0.2, 0.15, 0.13, 0.1, 0.07, 0.05]))

    credit_score = int(np.clip(np.random.normal(680, 85), 300, 900))

    # Risk score: inversely related to credit score, with noise
    risk_base = (900 - credit_score) / 600
    risk_score = float(np.clip(risk_base + np.random.normal(0, 0.12), 0, 1))

    # Default probability driven by risk score
    is_default = np.random.binomial(1, p=np.clip(risk_score * 0.35, 0.01, 0.9))

    # Claims only apply to a subset (insurance-linked loan products)
    has_claim = np.random.binomial(1, p=0.18)
    claim_status = None
    claim_amount = 0
    resolution_days = None
    if has_claim:
        claim_status = np.random.choice(
            ["Approved", "Rejected", "Pending", "Under Review"],
            p=[0.52, 0.18, 0.15, 0.15]
        )
        claim_amount = round(max(1000, np.random.lognormal(mean=np.log(35000), sigma=0.6)), 2)
        resolution_days = int(np.clip(np.random.normal(9, 4), 1, 45)) if claim_status in ("Approved", "Rejected") else None

    # Collections: for defaulted accounts, track days past due & collection outcome
    days_past_due = int(np.clip(np.random.exponential(scale=35), 0, 365)) if is_default else 0
    collected_flag = None
    if is_default:
        collected_flag = np.random.binomial(1, p=np.clip(0.75 - (days_past_due / 500), 0.15, 0.85))

    records.append({
        "account_id": f"ACC{100000 + i}",
        "region": region,
        "loan_type": loan_type,
        "channel": channel,
        "disbursement_date": disb_date.strftime("%Y-%m-%d"),
        "loan_amount": round(loan_amount, 2),
        "tenure_months": tenure_months,
        "credit_score": credit_score,
        "risk_score": round(risk_score, 4),
        "is_default": is_default,
        "days_past_due": days_past_due,
        "collected_flag": collected_flag,
        "has_claim": has_claim,
        "claim_status": claim_status,
        "claim_amount": claim_amount,
        "claim_resolution_days": resolution_days,
    })

df = pd.DataFrame(records)
df.to_csv("data/raw_bfsi_accounts.csv", index=False)
print(f"Generated {len(df)} synthetic BFSI account records -> data/raw_bfsi_accounts.csv")
print(df.head(3).to_string())

"""
build_dashboard_data.py
-------------------------
Runs the project's SQL analysis queries against the SQLite warehouse
and exports the results as a single JSON file consumed by the
interactive HTML dashboard (dashboard/index.html).

This mirrors a real BI workflow: SQL layer -> aggregated metrics ->
dashboard visualization layer.
"""

import json
import sqlite3
import pandas as pd
from pathlib import Path

DB_PATH = Path("data/bfsi.db")
OUT_PATH = Path("dashboard/dashboard_data.json")

conn = sqlite3.connect(DB_PATH)


def q(sql):
    return pd.read_sql_query(sql, conn)


# ---- KPI headline numbers ----
kpi = q("""
    SELECT
        COUNT(*) AS total_accounts,
        ROUND(SUM(loan_amount), 2) AS total_disbursed,
        ROUND(100.0 * SUM(is_default) / COUNT(*), 2) AS default_rate_pct,
        ROUND(100.0 * SUM(has_claim) / COUNT(*), 2) AS claim_incidence_pct,
        ROUND(AVG(risk_score), 4) AS avg_risk_score
    FROM accounts
""").iloc[0].to_dict()

collected = q("""
    SELECT ROUND(100.0 * SUM(collected_flag) / SUM(is_default), 2) AS collection_rate_pct
    FROM accounts WHERE is_default = 1
""").iloc[0].to_dict()
kpi["collection_rate_pct"] = collected["collection_rate_pct"]

# ---- Region performance ----
region = q("""
    SELECT region,
           COUNT(*) AS total_accounts,
           ROUND(SUM(loan_amount), 2) AS total_disbursed,
           ROUND(100.0 * SUM(is_default) / COUNT(*), 2) AS default_rate_pct,
           ROUND(100.0 * SUM(has_claim) / COUNT(*), 2) AS claim_incidence_pct
    FROM accounts GROUP BY region ORDER BY total_disbursed DESC
""")

# ---- Risk tier breakdown ----
risk_tier = q("""
    SELECT risk_tier,
           COUNT(*) AS accounts,
           ROUND(100.0 * SUM(is_default) / COUNT(*), 2) AS actual_default_rate_pct
    FROM accounts GROUP BY risk_tier
    ORDER BY CASE risk_tier
        WHEN 'Low Risk' THEN 0 WHEN 'Medium Risk' THEN 1
        WHEN 'High Risk' THEN 2 ELSE 3 END
""")

# ---- Monthly disbursement trend ----
trend = q("""
    SELECT strftime('%Y-%m', disbursement_date) AS month,
           COUNT(*) AS accounts_disbursed,
           ROUND(SUM(loan_amount), 2) AS total_disbursed
    FROM accounts GROUP BY month ORDER BY month
""")

# ---- Loan type mix ----
loan_type = q("""
    SELECT loan_type, COUNT(*) AS accounts, ROUND(SUM(loan_amount), 2) AS total_disbursed
    FROM accounts GROUP BY loan_type ORDER BY total_disbursed DESC
""")

# ---- Claims status breakdown ----
claims = q("""
    SELECT claim_status, COUNT(*) AS claim_count,
           ROUND(AVG(claim_resolution_days), 1) AS avg_resolution_days
    FROM accounts WHERE has_claim = 1 GROUP BY claim_status ORDER BY claim_count DESC
""")

# ---- Channel effectiveness ----
channel = q("""
    SELECT channel, COUNT(*) AS accounts,
           ROUND(100.0 * SUM(is_default) / COUNT(*), 2) AS default_rate_pct
    FROM accounts GROUP BY channel ORDER BY default_rate_pct ASC
""")

# ---- DPD collections funnel ----
dpd = q("""
    SELECT dpd_bucket, COUNT(*) AS defaulted_accounts,
           ROUND(100.0 * SUM(collected_flag) / COUNT(*), 2) AS collection_rate_pct
    FROM accounts WHERE is_default = 1 GROUP BY dpd_bucket
    ORDER BY CASE dpd_bucket
        WHEN 'Not Overdue' THEN 0 WHEN '1-30 Days' THEN 1
        WHEN '31-60 Days' THEN 2 WHEN '61-90 Days' THEN 3 ELSE 4 END
""")

data = {
    "kpi": kpi,
    "region": region.to_dict(orient="records"),
    "risk_tier": risk_tier.to_dict(orient="records"),
    "trend": trend.to_dict(orient="records"),
    "loan_type": loan_type.to_dict(orient="records"),
    "claims": claims.to_dict(orient="records"),
    "channel": channel.to_dict(orient="records"),
    "dpd": dpd.to_dict(orient="records"),
}

OUT_PATH.parent.mkdir(exist_ok=True)
with open(OUT_PATH, "w") as f:
    json.dump(data, f, indent=2, default=str)

print(f"[DONE] Dashboard data exported -> {OUT_PATH}")
print(f"KPIs: {kpi}")

conn.close()

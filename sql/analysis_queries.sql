-- ============================================================
-- analysis_queries.sql
-- SQL analysis layer for the BFSI Loan & Claims Analytics project
-- Run against the SQLite database produced by etl/etl_pipeline.py
-- ============================================================

-- 1. Portfolio overview: total disbursed amount, default rate, and
--    claims incidence by region
SELECT
    region,
    COUNT(*) AS total_accounts,
    ROUND(SUM(loan_amount), 2) AS total_disbursed,
    ROUND(AVG(risk_score), 4) AS avg_risk_score,
    ROUND(100.0 * SUM(is_default) / COUNT(*), 2) AS default_rate_pct,
    ROUND(100.0 * SUM(has_claim) / COUNT(*), 2) AS claim_incidence_pct
FROM accounts
GROUP BY region
ORDER BY total_disbursed DESC;

-- 2. Collections efficiency: percentage of defaulted accounts
--    successfully collected, segmented by days-past-due bucket
SELECT
    CASE
        WHEN days_past_due = 0 THEN 'Not Overdue'
        WHEN days_past_due BETWEEN 1 AND 30 THEN '1-30 Days'
        WHEN days_past_due BETWEEN 31 AND 60 THEN '31-60 Days'
        WHEN days_past_due BETWEEN 61 AND 90 THEN '61-90 Days'
        ELSE '90+ Days'
    END AS dpd_bucket,
    COUNT(*) AS defaulted_accounts,
    ROUND(100.0 * SUM(COALESCE(collected_flag, 0)) / COUNT(*), 2) AS collection_rate_pct
FROM accounts
WHERE is_default = 1
GROUP BY dpd_bucket
ORDER BY
    CASE dpd_bucket
        WHEN 'Not Overdue' THEN 0
        WHEN '1-30 Days' THEN 1
        WHEN '31-60 Days' THEN 2
        WHEN '61-90 Days' THEN 3
        ELSE 4
    END;

-- 3. Claims processing performance: approval rate and average
--    resolution time by claim status
SELECT
    claim_status,
    COUNT(*) AS claim_count,
    ROUND(AVG(claim_amount), 2) AS avg_claim_amount,
    ROUND(AVG(claim_resolution_days), 1) AS avg_resolution_days
FROM accounts
WHERE has_claim = 1
GROUP BY claim_status
ORDER BY claim_count DESC;

-- 4. Risk segmentation: bucket accounts into risk tiers and measure
--    default rate per tier (classic risk-scoring validation query)
SELECT
    CASE
        WHEN risk_score < 0.25 THEN 'Low Risk'
        WHEN risk_score < 0.50 THEN 'Medium Risk'
        WHEN risk_score < 0.75 THEN 'High Risk'
        ELSE 'Critical Risk'
    END AS risk_tier,
    COUNT(*) AS accounts,
    ROUND(100.0 * SUM(is_default) / COUNT(*), 2) AS actual_default_rate_pct,
    ROUND(AVG(credit_score), 0) AS avg_credit_score
FROM accounts
GROUP BY risk_tier
ORDER BY actual_default_rate_pct DESC;

-- 5. Monthly disbursement trend by loan type (time-series view,
--    powers the dashboard's trend chart)
SELECT
    strftime('%Y-%m', disbursement_date) AS month,
    loan_type,
    COUNT(*) AS accounts_disbursed,
    ROUND(SUM(loan_amount), 2) AS total_disbursed
FROM accounts
GROUP BY month, loan_type
ORDER BY month;

-- 6. Channel effectiveness: which acquisition channel brings the
--    healthiest (lowest-risk) accounts
SELECT
    channel,
    COUNT(*) AS accounts,
    ROUND(AVG(risk_score), 4) AS avg_risk_score,
    ROUND(100.0 * SUM(is_default) / COUNT(*), 2) AS default_rate_pct
FROM accounts
GROUP BY channel
ORDER BY default_rate_pct ASC;

-- MRR by month from Stripe invoices loaded into BigQuery
-- Assumes table: `project.dataset.stripe_invoices`

WITH paid_invoices AS (
  SELECT
    DATE_TRUNC(DATE(period_start), MONTH) AS month,
    amount_paid / 100.0 AS amount_usd
  FROM `project.dataset.stripe_invoices`
  WHERE status = 'paid'
),
monthly_mrr AS (
  SELECT
    month,
    SUM(amount_usd) AS mrr_amount
  FROM paid_invoices
  GROUP BY month
)
SELECT
  month,
  mrr_amount
FROM monthly_mrr
ORDER BY month;

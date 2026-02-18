-- Calculate Monthly Recurring Revenue (MRR) from active subscriptions
-- MRR = Global average monthly amount × number of active subscriptions per month

WITH 
-- Calculate global average monthly amount across all subscriptions
global_avg AS (
  SELECT
    AVG(monthly_amount / 100.0) AS avg_monthly_amount_usd
  FROM `static-rabbit-74213.stripe_mrr.subscriptions`
  WHERE monthly_amount > 0
),

-- Generate a series of months based on subscription data
month_series AS (
  SELECT DISTINCT
    DATE_TRUNC(DATE(created), MONTH) AS month
  FROM `static-rabbit-74213.stripe_mrr.subscriptions`
  UNION DISTINCT
  SELECT DISTINCT
    DATE_TRUNC(DATE(current_period_start), MONTH) AS month
  FROM `static-rabbit-74213.stripe_mrr.subscriptions`
),

-- For each month, find subscriptions that were active
active_subscriptions AS (
  SELECT
    m.month,
    s.subscription_id
  FROM month_series m
  CROSS JOIN `static-rabbit-74213.stripe_mrr.subscriptions` s
  WHERE 
    -- Subscription was created before or during this month
    DATE(s.created) <= LAST_DAY(m.month)
    -- AND subscription was still active (not canceled yet, or canceled after this month started)
    AND (
      s.canceled_at IS NULL 
      OR DATE(s.canceled_at) >= (m.month)
    )
    -- Only include subscriptions with actual monthly amounts
    AND s.monthly_amount > 0
),

-- Calculate MRR per month: global avg × number of active subscriptions
monthly_mrr AS (
  SELECT
    a.month,
    COUNT(DISTINCT a.subscription_id) AS active_subscriptions,
    g.avg_monthly_amount_usd,
    COUNT(DISTINCT a.subscription_id) * g.avg_monthly_amount_usd AS mrr_amount
  FROM active_subscriptions a
  CROSS JOIN global_avg g
  GROUP BY a.month, g.avg_monthly_amount_usd
)

SELECT
  FORMAT_DATE('%Y-%m', month) AS month,
  active_subscriptions,
  ROUND(avg_monthly_amount_usd, 2) AS avg_monthly_amount_usd,
  ROUND(mrr_amount, 2) AS mrr_amount
FROM monthly_mrr
ORDER BY month;

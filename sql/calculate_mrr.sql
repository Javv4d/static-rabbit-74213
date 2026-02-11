-- MRR (Monthly Recurring Revenue) Calculation Query
-- This query calculates various MRR metrics from subscription events

-- Create a base table with all subscription events
WITH subscription_events AS (
  SELECT
    event_id,
    customer_id,
    event_type,
    PARSE_DATE('%Y-%m-%d', event_date) AS event_date,
    plan_type,
    mrr
  FROM `project.dataset.subscription_events`
),

-- Calculate customer state at each event
customer_timeline AS (
  SELECT
    customer_id,
    event_date,
    event_type,
    mrr,
    LAG(mrr) OVER (PARTITION BY customer_id ORDER BY event_date) AS previous_mrr
  FROM subscription_events
),

-- Aggregate events by month
monthly_events AS (
  SELECT
    FORMAT_DATE('%Y-%m', event_date) AS month,
    customer_id,
    event_type,
    mrr,
    previous_mrr,
    CASE
      WHEN event_type = 'new_subscription' THEN mrr
      ELSE 0
    END AS new_mrr,
    CASE
      WHEN event_type = 'upgrade' THEN mrr - COALESCE(previous_mrr, 0)
      ELSE 0
    END AS expansion_mrr,
    CASE
      WHEN event_type = 'downgrade' THEN COALESCE(previous_mrr, 0) - mrr
      ELSE 0
    END AS contraction_mrr,
    CASE
      WHEN event_type = 'churn' THEN COALESCE(previous_mrr, mrr)
      ELSE 0
    END AS churn_mrr
  FROM customer_timeline
),

-- Calculate monthly aggregates
monthly_metrics AS (
  SELECT
    month,
    SUM(new_mrr) AS new_mrr,
    SUM(expansion_mrr) AS expansion_mrr,
    SUM(contraction_mrr) AS contraction_mrr,
    SUM(churn_mrr) AS churn_mrr,
    COUNT(DISTINCT CASE WHEN event_type = 'new_subscription' THEN customer_id END) AS new_customers,
    COUNT(DISTINCT CASE WHEN event_type = 'churn' THEN customer_id END) AS churned_customers
  FROM monthly_events
  GROUP BY month
),

-- Calculate running total MRR
mrr_with_totals AS (
  SELECT
    month,
    new_mrr,
    expansion_mrr,
    contraction_mrr,
    churn_mrr,
    new_mrr + expansion_mrr - contraction_mrr - churn_mrr AS net_new_mrr,
    SUM(new_mrr + expansion_mrr - contraction_mrr - churn_mrr) 
      OVER (ORDER BY month ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS total_mrr,
    new_customers,
    churned_customers
  FROM monthly_metrics
)

-- Final output
SELECT
  month,
  ROUND(total_mrr, 2) AS total_mrr,
  ROUND(new_mrr, 2) AS new_mrr,
  ROUND(expansion_mrr, 2) AS expansion_mrr,
  ROUND(contraction_mrr, 2) AS contraction_mrr,
  ROUND(churn_mrr, 2) AS churn_mrr,
  ROUND(net_new_mrr, 2) AS net_new_mrr,
  new_customers,
  churned_customers,
  -- Calculate growth rate
  ROUND(
    CASE 
      WHEN LAG(total_mrr) OVER (ORDER BY month) > 0 
      THEN ((total_mrr - LAG(total_mrr) OVER (ORDER BY month)) / LAG(total_mrr) OVER (ORDER BY month)) * 100
      ELSE 0
    END, 
    2
  ) AS growth_rate_percent
FROM mrr_with_totals
ORDER BY month;

-- MRR Calculation Query for SQLite
-- Simplified version for local development

-- Monthly MRR Metrics
SELECT
  month,
  total_mrr,
  new_mrr,
  expansion_mrr,
  contraction_mrr,
  churn_mrr,
  net_new_mrr,
  active_customers,
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
  ) AS growth_rate_percent,
  -- Calculate churn rate
  ROUND(
    CASE 
      WHEN LAG(active_customers) OVER (ORDER BY month) > 0 
      THEN (CAST(churned_customers AS REAL) / LAG(active_customers) OVER (ORDER BY month)) * 100
      ELSE 0
    END, 
    2
  ) AS churn_rate_percent
FROM mrr_metrics
ORDER BY month;

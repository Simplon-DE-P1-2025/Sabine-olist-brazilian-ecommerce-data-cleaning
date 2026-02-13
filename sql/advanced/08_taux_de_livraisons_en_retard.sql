
-- KPI “logistique” 
-- Taux de livraisons en retard (%) --> (delivered > estimated)

WITH orders_dates AS (
  SELECT
    order_id,
    MIN(delivered_date_id)  AS delivered_date_id,
    MIN(estimated_date_id)  AS estimated_date_id
  FROM fact_order_items
  WHERE delivered_date_id IS NOT NULL
    AND estimated_date_id IS NOT NULL
  GROUP BY order_id
),
flags AS (
  SELECT
    order_id,
    CASE WHEN delivered_date_id > estimated_date_id THEN 1 ELSE 0 END AS is_late
  FROM orders_dates
)
SELECT
  COUNT(*) AS commandes_livrées,
  SUM(is_late) AS commandes_en_retard,
  ROUND(100.0 * SUM(is_late) / COUNT(*), 2) AS taux_de_commandes_en_retard
FROM flags;

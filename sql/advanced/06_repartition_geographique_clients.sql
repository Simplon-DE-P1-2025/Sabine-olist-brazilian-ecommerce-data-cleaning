
-- KPI “géographie”
-- Répartition du CA par État (clients)

SELECT
  c.customer_state,
  COUNT(DISTINCT c.customer_id) AS clients,
  COUNT(DISTINCT f.order_id) AS commandes,
  ROUND(SUM(f.price + COALESCE(f.freight_value, 0)), 2) AS CA
FROM fact_order_items f
JOIN dim_customers c ON c.customer_id = f.customer_id
GROUP BY c.customer_state
ORDER BY CA DESC;

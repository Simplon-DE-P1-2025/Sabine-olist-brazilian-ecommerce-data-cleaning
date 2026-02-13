
-- Classement du top des vendeurs par chiffre d’affaires (CA)

SELECT
  s.seller_id,
  COUNT(DISTINCT f.order_id) AS orders,
  COUNT(*) AS items_sold,
  ROUND(SUM(f.price + COALESCE(f.freight_value, 0)), 2) AS revenue
FROM fact_order_items f
JOIN dim_sellers s ON s.seller_id = f.seller_id
GROUP BY s.seller_id
ORDER BY revenue DESC
LIMIT 15;


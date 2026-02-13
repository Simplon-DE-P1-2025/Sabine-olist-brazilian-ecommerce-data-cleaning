
-- Calcul du nombre de commandes par mois (purchase date)

SELECT
  d.year,
  d.month,
  COUNT(DISTINCT f.order_id) AS orders
FROM fact_order_items f
JOIN dim_date d ON d.date_id = f.date_id
GROUP BY d.year, d.month
ORDER BY d.year, d.month;
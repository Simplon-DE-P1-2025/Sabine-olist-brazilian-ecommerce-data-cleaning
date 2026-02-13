
-- Calcul du chiffre d’affaires par mois

SELECT
  d.year,
  d.month,
  ROUND(SUM(f.price + COALESCE(f.freight_value, 0)), 2) AS CA
FROM fact_order_items f
JOIN dim_date d
  ON d.date_id = f.purchase_date_id
GROUP BY d.year, d.month
ORDER BY d.year, d.month;



-- Classement du top des catégories de produits par chiffre d’affaires (CA)

SELECT
  p.product_category_name AS categorie,
  COUNT(*) AS nb_articles_vendus,
  COUNT(DISTINCT f.order_id) AS commandes,
  ROUND(SUM(f.price + COALESCE(f.freight_value, 0)), 2) AS CA
FROM fact_order_items f
JOIN dim_products p ON p.product_id = f.product_id
GROUP BY p.product_category_name
ORDER BY CA DESC
LIMIT 15;

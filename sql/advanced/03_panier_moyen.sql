
-- Calcul du panier moyen par commande

WITH par_commande AS (
  SELECT
    f.order_id,
    SUM(f.price + COALESCE(f.freight_value, 0)) AS montant_de_commande
  FROM fact_order_items f
  GROUP BY f.order_id
)
SELECT
  ROUND(AVG(montant_de_commande), 2) AS panier_moyen,
  ROUND(MIN(montant_de_commande), 2) AS panier_min,
  ROUND(MAX(montant_de_commande), 2) AS panier_max
FROM par_commande;

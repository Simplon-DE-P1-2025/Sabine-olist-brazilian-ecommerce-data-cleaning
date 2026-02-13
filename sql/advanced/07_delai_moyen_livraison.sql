
-- KPI “logistique” 
-- Délai moyen réel de livraison (jours, livraison - achat), au niveau commande

WITH orders_dates AS (
  SELECT
    order_id,
    MIN(purchase_date_id)   AS purchase_date_id,
    MIN(delivered_date_id)  AS delivered_date_id
  FROM fact_order_items
  WHERE delivered_date_id IS NOT NULL
  GROUP BY order_id
)
SELECT
  ROUND(AVG(
    julianday(
      substr(delivered_date_id,1,4) || '-' || substr(delivered_date_id,5,2) || '-' || substr(delivered_date_id,7,2)
    ) -
    julianday(
      substr(purchase_date_id,1,4) || '-' || substr(purchase_date_id,5,2) || '-' || substr(purchase_date_id,7,2)
    )
  ), 2) AS avg_delivery_days
FROM orders_dates;


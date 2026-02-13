
-- Retard moyen de livraison (jours) = delivered − estimated (filtré sur retard)
-- Fonction julianday [date convertie en un nombre de jours]

WITH orders_dates AS (
  SELECT
    order_id, 
    MIN(delivered_date_id)  AS delivered_date_id,
    MIN(estimated_date_id)  AS estimated_date_id
  FROM fact_order_items
  WHERE delivered_date_id IS NOT NULL
    AND estimated_date_id IS NOT NULL
  GROUP BY order_id
)
SELECT
  ROUND(AVG(
    julianday(
      substr(delivered_date_id,1,4) || '-' || substr(delivered_date_id,5,2) || '-' || substr(delivered_date_id,7,2)
    ) -
    julianday(
      substr(estimated_date_id,1,4) || '-' || substr(estimated_date_id,5,2) || '-' || substr(estimated_date_id,7,2)
    )
  ), 2) AS avg_late_days
FROM orders_dates
WHERE delivered_date_id > estimated_date_id;



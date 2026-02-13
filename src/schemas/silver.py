# ============================================
# SCHEMAS SILVER (Pandera)
# ============================================
# Niveau Silver = typage correct et cohérent.
# Pandera avec coerce=True applique automatiquement :
#
#    • Conversion des identifiants → string
#    • Conversion des dates → datetime
#    • Conversion des montants → float
#    • Conversion des entiers → Int64 (entier nullable)
#
# Objectif :
#    - Garantir un typage strict et propre.
#    - Rendre la donnée exploitable pour Gold (modèle étoile).
#    - Supprimer les conversions manuelles (astype, to_datetime, to_numeric).
#    - Assurer une qualité minimale : ranges, formats, nullables.
#
# Le niveau Silver valide la donnée prête pour la modélisation Gold.

# ============================================


import pandera.pandas as pa
from pandera.pandas import Column, DataFrameSchema, Check


# ==========================
# CLIENTS
# ==========================
schema_customers_silver = DataFrameSchema(
    {
        "customer_id": Column(pa.String),
        "customer_unique_id": Column(pa.String, nullable=True),
        "customer_zip_code_prefix": Column(pa.Int, nullable=True),
        "customer_city": Column(pa.String, nullable=True),
        "customer_state": Column(pa.String, nullable=True),
    },
    coerce=True
)


# ==========================
# COMMANDES
# ==========================
schema_orders_silver = DataFrameSchema(
    {
        "order_id": Column(pa.String),
        "customer_id": Column(pa.String, nullable=True),
        "order_status": Column(pa.String, nullable=True),

        # toutes les dates converties par coerce=True
        "order_purchase_timestamp": Column(pa.DateTime, nullable=True),
        "order_approved_at": Column(pa.DateTime, nullable=True),
        "order_delivered_carrier_date": Column(pa.DateTime, nullable=True),
        "order_delivered_customer_date": Column(pa.DateTime, nullable=True),
        "order_estimated_delivery_date": Column(pa.DateTime, nullable=True),
    },
    coerce=True
)


# ==========================
# ARTICLES DE COMMANDE
# ==========================
schema_order_items_silver = DataFrameSchema(
    {
        "order_id": Column(pa.String),
        "order_item_id": Column(pa.Int, nullable=True),
        "product_id": Column(pa.String, nullable=True),
        "seller_id": Column(pa.String, nullable=True),

        "shipping_limit_date": Column(pa.DateTime, nullable=True),
        "price": Column(pa.Float, nullable=True),
        "freight_value": Column(pa.Float, nullable=True),
    },
    coerce=True
)


# ==========================
# PAIEMENTS (AUXILIAIRE)
# ==========================
schema_order_payments_silver = DataFrameSchema(
    {
        "order_id": Column(pa.String),
        "payment_sequential": Column(pa.Int, nullable=True),
        "payment_type": Column(pa.String, nullable=True),
        "payment_installments": Column(pa.Int, nullable=True),
        "payment_value": Column(pa.Float, nullable=True),
    },
    coerce=True
)


# ==========================
# AVIS CLIENTS (AUXILIAIRE)
# ==========================
schema_order_reviews_silver = DataFrameSchema(
    {
        "review_id": Column(pa.String),
        "order_id": Column(pa.String, nullable=True),
        "review_score": Column(pa.Int, Check.in_range(1, 5), nullable=True),

        "review_comment_title": Column(pa.String, nullable=True),
        "review_comment_message": Column(pa.String, nullable=True),

        "review_creation_date": Column(pa.DateTime, nullable=True),
        "review_answer_timestamp": Column(pa.DateTime, nullable=True),
    },
    coerce=True
)


# ==========================
# PRODUITS
# ==========================

schema_products_silver = DataFrameSchema(
    {
        "product_id": Column(pa.String),
        "product_category_name": Column(pa.String, nullable=True),

        "product_name_lenght": Column(pa.Int, nullable=True),
        "product_description_lenght": Column(pa.Int, nullable=True),
        "product_photos_qty": Column(pa.Int, nullable=True),

        "product_weight_g": Column(pa.Float, nullable=True),
        "product_length_cm": Column(pa.Float, nullable=True),
        "product_height_cm": Column(pa.Float, nullable=True),
        "product_width_cm": Column(pa.Float, nullable=True),
    },
    coerce=True
)


# ==========================
# VENDEURS
# ==========================
schema_sellers_silver = DataFrameSchema(
    {
        "seller_id": Column(pa.String),
        "seller_zip_code_prefix": Column(pa.Int, nullable=True),
        "seller_city": Column(pa.String, nullable=True),
        "seller_state": Column(pa.String, nullable=True),
    },
    coerce=True
)


# ==========================
# GEOLOCATION (nettoyée)
# ==========================
schema_geolocation_silver = DataFrameSchema(
    {
        "geolocation_zip_code_prefix": Column(pa.Int),
        "geolocation_lat": Column(pa.Float, nullable=True),
        "geolocation_lng": Column(pa.Float, nullable=True),
        "geolocation_city": Column(pa.String, nullable=True),
        "geolocation_state": Column(pa.String, nullable=True),
    },
    coerce=True
)


# ==========================
# PRODUIT → TRADUCTION
# ==========================
schema_category_translation_silver = DataFrameSchema(
    {
        "product_category_name": Column(pa.String),
        "product_category_name_english": Column(pa.String, nullable=True),
    },
    coerce=True
)
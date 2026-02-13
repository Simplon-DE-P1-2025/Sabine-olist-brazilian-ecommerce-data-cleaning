# ============================================
# SCHEMAS GOLD (Pandera)
# ============================================
# Niveau Gold = validation stricte pour le modèle étoile.
#
# Le niveau Gold est le point d’entrée pour les analyses SQL avancées.
#
# Objectifs :
# ----------
#    • Garantir l’unicité des clés primaires (PK).
#    • Garantir des types stricts et cohérents.
#    • Vérifier la cohérence des dimensions et de la fact.
#    • Préparer les données pour le chargement SQLite (schema_etoile.sql).
#    • Tables auxiliaires prêtes pour SQL avancé (order_payments, order_reviews).
#
# coerce=True : conversions automatiques (string, datetime, float, Int64)
#
# ============================================




# src/schemas/gold.py

import pandera.pandas as pa
from pandera.pandas import Column, DataFrameSchema, Check

# ============================================
# SCHEMAS GOLD (Pandera)
# ============================================
# Niveau Gold = validation stricte pour le modèle étoile.
# Objectif :
#   • Unicité des PK
#   • Types stricts et cohérents
#   • Cohérence dims/fact
#   • Tables auxiliaires prêtes pour SQL avancé
# coerce=True : conversions automatiques (string, datetime, float, Int64)
#
# ============================================


# -------- DIM CUSTOMERS --------
schema_dim_customers = DataFrameSchema(
    {
        "customer_id": Column(pa.String, nullable=False),
        "customer_city": Column(pa.String, nullable=True),
        "customer_state": Column(pa.String, nullable=True),
    },
    coerce=True,
    unique=["customer_id"]
)


# -------- DIM PRODUCTS --------
schema_dim_products = DataFrameSchema(
    {
        "product_id": Column(pa.String, nullable=False),
        "product_category_name": Column(pa.String, nullable=True),
        "product_category_name_english": Column(pa.String, nullable=True),
    },
    coerce=True,
    unique=["product_id"]
)


# -------- DIM SELLERS --------
schema_dim_sellers = DataFrameSchema(
    {
        "seller_id": Column(pa.String, nullable=False),
        "seller_zip_code_prefix": Column(pa.Int, nullable=True),
        "seller_city": Column(pa.String, nullable=True),
        "seller_state": Column(pa.String, nullable=True),
    },
    coerce=True,
    unique=["seller_id"]
)


# -------- DIM DATE --------
schema_dim_date = DataFrameSchema(
    {
        "date_id": Column(pa.Int, nullable=False),
        "date": Column(pa.DateTime, nullable=False),
        "year": Column(pa.Int, nullable=False),
        "month": Column(pa.Int, nullable=False),
        "day": Column(pa.Int, nullable=False),
    },
    coerce=True,
    unique=["date_id"]
)


# -------- FACT ORDERS --------
schema_fact_orders = DataFrameSchema(
    {
        "order_id": Column(pa.String, nullable=False),
        "customer_id": Column(pa.String, nullable=False),

        "purchase_date_id": Column(pa.Int, nullable=False),

        "order_status": Column(pa.String, nullable=True),

        "order_purchase_timestamp": Column(pa.DateTime, nullable=True),
        "order_approved_at": Column(pa.DateTime, nullable=True),
        "order_delivered_carrier_date": Column(pa.DateTime, nullable=True),
        "order_delivered_customer_date": Column(pa.DateTime, nullable=True),
        "order_estimated_delivery_date": Column(pa.DateTime, nullable=True),
    },
    coerce=True,
    unique=["order_id"],
)



# -------- FACT ORDER ITEMS --------
schema_fact_order_items = DataFrameSchema(
    {
        "order_id": Column(pa.String, nullable=False),
        "order_item_id": Column(pa.Int, nullable=False),
        "product_id": Column(pa.String, nullable=False),
        "seller_id": Column(pa.String, nullable=False),
        "customer_id": Column(pa.String, nullable=False),

        "shipping_limit_date": Column(pa.DateTime, nullable=True),
        "price": Column(pa.Float, nullable=True),
        "freight_value": Column(pa.Float, nullable=True),

        "purchase_date_id": Column(pa.Int, nullable=False),
        "shipping_limit_date_id": Column(pa.Int, nullable=True),
    },
    coerce=True,
    unique=[["order_id", "order_item_id"]],
)



# -------- TABLE AUX PAYMENTS --------
schema_order_payments_gold = DataFrameSchema(
    {
        "order_id": Column(pa.String, nullable=False),
        "payment_sequential": Column(pa.Int, nullable=True),
        "payment_type": Column(pa.String, nullable=True),
        "payment_installments": Column(pa.Int, nullable=True),
        "payment_value": Column(pa.Float, nullable=True),
    },
    coerce=True
)


# -------- TABLE AUX REVIEWS --------
schema_order_reviews_gold = DataFrameSchema(
    {
        "review_id": Column(pa.String, nullable=False),
        "order_id": Column(pa.String, nullable=True),
        "review_score": Column(pa.Int, Check.in_range(1, 5), nullable=True),
        "review_creation_date": Column(pa.DateTime, nullable=True),
        "review_answer_timestamp": Column(pa.DateTime, nullable=True),
        "review_comment_title": Column(pa.String, nullable=True),
        "review_comment_message": Column(pa.String, nullable=True),
    },
    coerce=True,
    unique=["review_id"]
)
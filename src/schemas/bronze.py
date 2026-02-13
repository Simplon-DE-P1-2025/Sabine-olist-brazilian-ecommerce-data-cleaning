# ============================================
# SCHEMAS BRONZE (Pandera)
# ============================================

# Niveau Bronze = validation minimale.
#
# Objectif :
#   - Vérifier la présence des colonnes attendues.
#   - Accepter les types tels que lus dans les CSV (object, string, float…).
#   - Ne réaliser AUCUNE conversion de type (coerce=False).
#   - Ne pas bloquer les valeurs manquantes.
#   - Préparer les données au typage Silver.
#
# Le niveau Bronze sert uniquement à garantir
# que la structure tabulaire brute est saine et exploitable.

# ============================================

import pandas as pd
import pandera.pandas as pa
from pandera.pandas import Column, DataFrameSchema, Check 


# ==========================
# CLIENTS
# ==========================

schema_customers_bronze = DataFrameSchema(
    {
        "customer_id": Column(pa.String, nullable=False),
        "customer_unique_id": Column(pa.String, nullable=True),
        # ⚠️ zip codes : souvent mieux en texte pour préserver les zéros en tête
        "customer_zip_code_prefix": Column(pa.String, nullable=False),
        "customer_city": Column(pa.String, nullable=False),
        "customer_state": Column(pa.String, nullable=False),
    },
    coerce=True  # <-- important pour éviter les mismatches
)


# ==========================
# COMMANDES
# ==========================

ORDER_STATUS_ALLOWED = [
    "created", "approved", "invoiced", "processing", "shipped",
    "delivered", "canceled", "unavailable"
]

schema_orders_bronze = DataFrameSchema(
    {
        "order_id": Column(pa.String, nullable=False),
        "customer_id": Column(pa.String, nullable=True),  # aligné avec customers
        "order_status": Column(pa.String, nullable=True, checks=Check.isin(ORDER_STATUS_ALLOWED)),
        "order_purchase_timestamp": Column(pa.Timestamp, nullable=True),
        "order_approved_at": Column(pa.Timestamp, nullable=True),
        "order_delivered_carrier_date": Column(pa.Timestamp, nullable=True),
        "order_delivered_customer_date": Column(pa.Timestamp, nullable=True),
        "order_estimated_delivery_date": Column(pa.Timestamp, nullable=True),
    },
    coerce=True,   # conversions automatiques vers les dtypes déclarés
    strict=False,  # True une fois le pipeline stabilisé 
)


# ==========================
# ARTICLES DE COMMANDE
# ==========================


schema_order_items_bronze = DataFrameSchema(
{
        "order_id": Column(pa.String, nullable=False),         # aligné avec orders
        "order_item_id": Column(pa.Int64, nullable=True,       # entier nullable (pandas "Int64")
                                checks=Check.ge(1)),           # items commencent à 1 dans Olist
        "product_id": Column(pa.String, nullable=True),
        "seller_id": Column(pa.String, nullable=True),
        "shipping_limit_date": Column(pa.Timestamp, nullable=True),
        "price": Column(pa.Float64, nullable=True,
                        checks=Check.ge(0.0)),
        "freight_value": Column(pa.Float64, nullable=True,
                                checks=Check.ge(0.0)),
    },
coerce=True,
strict=False,   # True une fois le pipeline stabilisé
)



# ==========================
# PAIEMENTS (AUXILIAIRE)
# ==========================

PAYMENT_TYPES_ALLOWED = [
    "credit_card", "boleto", "voucher", "debit_card", "not_defined"
]

schema_order_payments_bronze = DataFrameSchema(
    {
        "order_id": Column(pa.String, nullable=False),
        "payment_sequential": Column(pa.Int64, nullable=True, checks=Check.ge(1)),
        "payment_type": Column(pa.String, nullable=True, checks=Check.isin(PAYMENT_TYPES_ALLOWED)),
        "payment_installments": Column(pa.Int64, nullable=True, checks=Check.ge(0)),
        "payment_value": Column(pa.Float64, nullable=True, checks=Check.ge(0.0)),
    },
    coerce=True,   # évite les mismatchs de dtypes
    strict=False,  # True une fois le pipeline stabilisé
)

# ==========================
# AVIS CLIENTS (AUXILIAIRE)
# ==========================

schema_order_reviews_bronze = DataFrameSchema(
    {
        "review_id": Column(pa.String, nullable=False),
        "order_id": Column(pa.String, nullable=True),  # aligné avec orders
        "review_score": Column(
            pa.Int64, nullable=True,
            checks=Check.in_range(1, 5, include_min=True, include_max=True),
        ),
        "review_comment_title": Column(pa.String, nullable=True),
        "review_comment_message": Column(pa.String, nullable=True),
        "review_creation_date": Column(pa.Timestamp, nullable=True),
        "review_answer_timestamp": Column(pa.Timestamp, nullable=True),
    },
    checks=[
        # Cohérence temporelle : si les deux dates existent, la réponse ne doit pas précéder la création
        Check(
            lambda df: (
                df[["review_creation_date", "review_answer_timestamp"]]
                .apply(
                    lambda row: (
                        True
                        if (pd.isna(row["review_creation_date"]) or pd.isna(row["review_answer_timestamp"]))
                        else row["review_answer_timestamp"] >= row["review_creation_date"]
                    ),
                    axis=1,
                )
            ).all(),
            error="review_answer_timestamp doit être >= review_creation_date (quand les deux sont présentes).",
        ),
    ],
    coerce=True,
    strict=False,  # True une fois le pipeline stabilisé
)

# ==========================
# PRODUITS
# ==========================

schema_products_bronze = DataFrameSchema(
    {
        "product_id": Column(pa.String, nullable=False),
        "product_category_name": Column(pa.String, nullable=True),

        # Entier nullable (pandas "Int64"), pas "int64"
        "product_name_lenght": Column(pa.Int, nullable=True, checks=Check.ge(0)),
        "product_description_lenght": Column(pa.Int, nullable=True, checks=Check.ge(0)),
        "product_photos_qty": Column(pa.Int, nullable=True, checks=Check.ge(0)),
        "product_weight_g": Column(pa.Float64, nullable=True, checks=[Check.ge(0.0), Check.le(100000.0)]),
        "product_length_cm": Column(pa.Float64, nullable=True, checks=[Check.ge(0.0), Check.le(200.0)]),
        "product_height_cm": Column(pa.Float64, nullable=True, checks=[Check.ge(0.0), Check.le(200.0)]),
        "product_width_cm": Column(pa.Float64, nullable=True, checks=[Check.ge(0.0), Check.le(200.0)]),
    },
    coerce=True,   # laisse Pandera convertir automatiquement
    strict=False,
)

# ==========================
# VENDEURS
# ==========================

# États brésiliens (UF) + DF
BRAZIL_STATES = [
    "AC","AL","AP","AM","BA","CE","DF","ES","GO","MA","MT","MS","MG",
    "PA","PB","PR","PE","PI","RJ","RN","RS","RO","RR","SC","SP","SE","TO"
]

schema_sellers_bronze = DataFrameSchema(
    {
        "seller_id": Column(pa.String, nullable=False),
        # ZIP en string : évite la perte des zéros en tête. On peut contrôler le format.
        "seller_zip_code_prefix": Column(
            pa.String, nullable=True,
            checks=[
                # Optionnel : que des chiffres (si non nul)
                Check(lambda s: s.dropna().str.fullmatch(r"\d+").all(), error="ZIP doit être numérique (si présent)"),
                # Optionnel : longueur plausible (Olist fournit un préfixe, souvent 5)
                Check(lambda s: s.dropna().str.len().between(3, 8).all(), error="Longueur ZIP entre 3 et 8"),
            ]
        ),
        "seller_city": Column(pa.String, nullable=True),
        "seller_state": Column(pa.String, nullable=True, checks=Check.isin(BRAZIL_STATES)),
    },
    coerce=True,     # conversions auto vers les dtypes déclarés
    strict=False,    # True quand c’est stabilisé pour bloquer les colonnes en trop
)


# ==========================
# GEOLOCATION
# ==========================

BRAZIL_STATES = [
    "AC","AL","AP","AM","BA","CE","DF","ES","GO","MA","MT","MS","MG",
    "PA","PB","PR","PE","PI","RJ","RN","RS","RO","RR","SC","SP","SE","TO"
]

schema_geolocation_bronze = DataFrameSchema(
    {
        # ZIP prefix en string : préserve les zéros en tête
        "geolocation_zip_code_prefix": Column(
            pa.String, nullable=False,
            checks=[
                # uniquement des chiffres
                Check(lambda s: s.str.fullmatch(r"\d+").all(),
                      error="geolocation_zip_code_prefix doit être numérique"),
                # longueur plausible (Olist utilise un préfixe, souvent 5)
                Check(lambda s: s.str.len().between(3, 8).all(),
                      error="Longueur du préfixe ZIP attendue entre 3 et 8"),
            ],
        ),
        "geolocation_lat": Column(
            pa.Float64, nullable=True,
            checks=[Check.ge(-90.0), Check.le(90.0)],
        ),
        "geolocation_lng": Column(
            pa.Float64, nullable=True,
            checks=[Check.ge(-180.0), Check.le(180.0)],
        ),
        "geolocation_city": Column(pa.String, nullable=True),
        "geolocation_state": Column(
            pa.String, nullable=True,
            checks=Check.isin(BRAZIL_STATES),
        ),
    },
    coerce=True,   # conversions auto vers les dtypes déclarés
    strict=False,  # True quand c’est stabilisé pour bloquer les colonnes en trop
)

# ==========================
# PRODUIT → TRADUCTION
# ==========================

schema_category_translation_bronze = DataFrameSchema(
    {
        "product_category_name": Column(
            pa.String,
            nullable=False,
            checks=[
                Check(lambda s: s.str.strip().ne(""), error="product_category_name ne doit pas être vide"),
                Check(lambda s: s.str.len().ge(1), error="Longueur minimale de 1 caractère"),
            ],
        ),
        "product_category_name_english": Column(
            pa.String,
            nullable=True,
            checks=[
                Check(lambda s: s.dropna().str.strip().ne(""), 
                      error="product_category_name_english ne doit pas être vide (si présent)"),
            ],
        ),
    },
    coerce=True,
    strict=False
)
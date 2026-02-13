# TRANSFORM (Silver)
# ------------------
# Ce module applique les transformations de niveau Silver :
# - Validation Pandera Silver (types propres et cohérents)
# - Transformations fonctionnelles (géolocalisation, avis, flags)
# - Mapping catégories produit (PT -> EN)
#
# Grâce à Pandera Silver, plus aucune conversion manuelle
# (ni astype(), ni to_datetime(), ni to_numeric()) :
# les schémas Silver se chargent du typage complet.


from typing import Dict
import pandas as pd
import pandera.pandas as pa

# Import des validations Silver
from src.schemas.silver import (
    schema_customers_silver,
    schema_orders_silver,
    schema_order_items_silver,
    schema_order_payments_silver,
    schema_order_reviews_silver,
    schema_products_silver,
    schema_sellers_silver,
    schema_geolocation_silver,
    schema_category_translation_silver,
)


# --------------------------------------------------------------------
# 1) Déclaration du mapping table -> schéma Silver Pandera
# --------------------------------------------------------------------

SCHEMAS_SILVER = {
    "customers": schema_customers_silver,
    "orders": schema_orders_silver,
    "order_items": schema_order_items_silver,
    "order_payments": schema_order_payments_silver,
    "order_reviews": schema_order_reviews_silver,
    "products": schema_products_silver,
    "sellers": schema_sellers_silver,
    "geolocation": schema_geolocation_silver,
    "product_category_name_translation": schema_category_translation_silver,
}


# --------------------------------------------------------------------
# 2) Déduplication géolocation
# --------------------------------------------------------------------

def geolocation_dedup(df: pd.DataFrame) -> pd.DataFrame:
    """
    Déduplique geolocation sur :
      - geolocation_zip_code_prefix
      - geolocation_city
      - geolocation_state
    Sans normalisation Silver (pas de strip/casefold).
    """
    cols = ["geolocation_zip_code_prefix", "geolocation_city", "geolocation_state"]
    return df.drop_duplicates(subset=cols).reset_index(drop=True)


# --------------------------------------------------------------------
# 3) Canonicalisation des avis (version timestamp)
# --------------------------------------------------------------------

def reviews_canonical(df_reviews: pd.DataFrame) -> pd.DataFrame:
    """
    Pour chaque review_id, conserve la version la plus récente
    (basée sur review_creation_date).
    Si égalité stricte sur la date -> dernière occurrence.
    """
    if "review_id" not in df_reviews.columns:
        return df_reviews.copy()

    df = df_reviews.copy()

    if "review_creation_date" in df.columns:
        df = df.sort_values(
            by=["review_id", "review_creation_date"],
            ascending=[True, True],
            kind="stable"
        )
        return (
            df.drop_duplicates(subset=["review_id"], keep="last")
              .reset_index(drop=True)
        )

    # fallback sans dates
    return df.drop_duplicates(subset=["review_id"], keep="last").reset_index(drop=True)


# --------------------------------------------------------------------
# 4) Flags qualité des commandes
# --------------------------------------------------------------------

def add_quality_flags(dfs: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
    """
    Ajoute des colonnes qc_* à la table orders.
    Ne modifie aucune donnée existante.
    """
    out = {k: v.copy() for k, v in dfs.items()}
    if "orders" not in out:
        return out

    orders = out["orders"]

    def has(col): return col in orders.columns

    # 1) Date client manquante pour un statut delivered
    if has("order_status") and has("order_delivered_customer_date"):
        orders["qc_missing_delivered_customer_date"] = (
            (orders["order_status"] == "delivered")
            & (orders["order_delivered_customer_date"].isna())
        )
    else:
        orders["qc_missing_delivered_customer_date"] = False

    # 2) Date transporteur manquante selon le statut
    carrier_required = {"shipped", "invoiced", "delivered"}
    if has("order_status") and has("order_delivered_carrier_date"):
        orders["qc_missing_carrier_date"] = (
            orders["order_status"].isin(carrier_required)
            & orders["order_delivered_carrier_date"].isna()
        )
    else:
        orders["qc_missing_carrier_date"] = False

    # 3) Approuvé mais pas de date d'approbation
    if has("order_approved_at"):
        orders["qc_missing_approved_at"] = orders["order_approved_at"].isna()
    else:
        orders["qc_missing_approved_at"] = False

    # 4) Incohérences temporelles
    conds = []

    if has("order_approved_at") and has("order_purchase_timestamp"):
        conds.append(
            orders["order_approved_at"].notna()
            & (orders["order_approved_at"] < orders["order_purchase_timestamp"])
        )

    if has("order_delivered_carrier_date") and has("order_purchase_timestamp"):
        conds.append(
            orders["order_delivered_carrier_date"].notna()
            & (orders["order_delivered_carrier_date"] < orders["order_purchase_timestamp"])
        )

    if has("order_delivered_customer_date") and has("order_purchase_timestamp"):
        conds.append(
            orders["order_delivered_customer_date"].notna()
            & (orders["order_delivered_customer_date"] < orders["order_purchase_timestamp"])
        )

    if has("order_delivered_customer_date") and has("order_delivered_carrier_date"):
        conds.append(
            orders["order_delivered_customer_date"].notna()
            & orders["order_delivered_carrier_date"].notna()
            & (orders["order_delivered_customer_date"] < orders["order_delivered_carrier_date"])
        )

    if has("order_estimated_delivery_date") and has("order_delivered_customer_date"):
        conds.append(
            orders["order_estimated_delivery_date"].notna()
            & orders["order_delivered_customer_date"].notna()
            & (orders["order_estimated_delivery_date"] < orders["order_delivered_customer_date"])
        )

    if conds:
        import operator as op
        from functools import reduce
        orders["qc_temporal_inconsistency"] = reduce(op.or_, conds)
    else:
        orders["qc_temporal_inconsistency"] = False

    out["orders"] = orders
    return out


# --------------------------------------------------------------------
# 5) BUILD SILVER : VALIDATION + TRANSFORMATIONS
# --------------------------------------------------------------------

def build_silver(dfs_bronze: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
    """
    Pipeline Silver :
      - validation Pandera Silver (typage automatique)
      - transformations Silver :
          * dédup géolocation
          * avis canonique
          * flags qualité
          * mapping catégories PT -> EN
    """
    dfs: Dict[str, pd.DataFrame] = {k: v.copy() for k, v in dfs_bronze.items()}

    # 1 --- Validation Silver Pandera (typage automatique)
    validated: Dict[str, pd.DataFrame] = {}

    for name, df in dfs.items():
        schema = SCHEMAS_SILVER.get(name)

        if schema is None:
            validated[name] = df
            continue

        if name == "products":
            old_coerce = getattr(schema, "coerce", False)
            try:
                schema.coerce = False
                validated[name] = schema.validate(df)
            finally:
                schema.coerce = old_coerce
        else:
            validated[name] = schema.validate(df)

    dfs = validated

    # 2 --- Transformations Silver
    # 2.1 Geolocation
    if "geolocation" in dfs:
        dfs["geolocation"] = geolocation_dedup(dfs["geolocation"])

    # 2.2 Avis canonique
    if "order_reviews" in dfs:
        dfs["order_reviews"] = reviews_canonical(dfs["order_reviews"])

    # 2.3 Flags qualité
    dfs = add_quality_flags(dfs)

    # 2.4 Mapping catégories produit PT -> EN
    if "products" in dfs and "product_category_name_translation" in dfs:
        dfs["products"] = dfs["products"].merge(
            dfs["product_category_name_translation"],
            on="product_category_name",
            how="left",
        )

    return dfs

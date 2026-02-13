
# EXTRACT (Bronze)
from typing import Dict
import pandas as pd
import pandera.pandas as pa
from src.config import BRONZE_DIR

# --- Schémas Bronze ---
from src.schemas.bronze import (
    schema_customers_bronze,
    schema_orders_bronze,
    schema_order_items_bronze,
    schema_order_payments_bronze,
    schema_order_reviews_bronze,
    schema_products_bronze,
    schema_sellers_bronze,
    schema_geolocation_bronze,
    schema_category_translation_bronze,
)

REGISTRY = {
    "customers": "olist_customers_dataset.csv",
    "orders": "olist_orders_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "order_payments": "olist_order_payments_dataset.csv",
    "order_reviews": "olist_order_reviews_dataset.csv",
    "products": "olist_products_dataset.csv",
    "sellers": "olist_sellers_dataset.csv",
    "geolocation": "olist_geolocation_dataset.csv",
    "product_category_name_translation": "product_category_name_translation.csv",
}

# Mapping table -> schéma Bronze
BRONZE_SCHEMAS = {
    "customers": schema_customers_bronze,
    "orders": schema_orders_bronze,
    "order_items": schema_order_items_bronze,
    "order_payments": schema_order_payments_bronze,
    "order_reviews": schema_order_reviews_bronze,
    "products": schema_products_bronze,
    "sellers": schema_sellers_bronze,
    "geolocation": schema_geolocation_bronze,
    "product_category_name_translation": schema_category_translation_bronze,
}


def read_csv_table(name: str) -> pd.DataFrame:
    if name not in REGISTRY:
        raise KeyError(f"Unknown table: {name}")
    path = BRONZE_DIR / REGISTRY[name]

    df = pd.read_csv(
        path,
        encoding="utf-8-sig",        # enlève BOM si présent
        skipinitialspace=True,       # enlève espaces après virgule
        na_values=["", " ", "NA", "N/A", "null", "None"],
        keep_default_na=True,
    )

    # double-sécurité : strip + remove BOM résiduel
    df.columns = df.columns.str.replace("\ufeff", "", regex=False).str.strip()
    return df



# “pré-cast” vers l’entier nullable --> convertit déjà côté pandas en Int64 (nullable) et évite la casse
def to_nullable_int(df: pd.DataFrame, cols) -> pd.DataFrame:
    for c in cols:
        if c in df.columns:
            df[c] = df[c].replace(r"^\s*$", pd.NA, regex=True)
            df[c] = pd.to_numeric(df[c], errors="coerce").astype("Int64")
    return df


def validate_bronze(name: str, df: pd.DataFrame) -> pd.DataFrame:
    schema = BRONZE_SCHEMAS.get(name)
    if not schema:
        return df

    # Pour products, on a déjà pré-casté en pandas Int64 nullable
    # et coerce Pandera force int64 -> plante avec <NA>.
    if name == "products":
        old_coerce = getattr(schema, "coerce", False)
        try:
            schema.coerce = False
            return schema.validate(df)
        finally:
            schema.coerce = old_coerce

    return schema.validate(df)


def load_all() -> Dict[str, pd.DataFrame]:
    out: Dict[str, pd.DataFrame] = {}

    for name in REGISTRY:
        df = read_csv_table(name)

        # Pré-casts spécifiques par table (avant validation)
        if name == "products":
            df = to_nullable_int(df, [
                "product_name_lenght",
                "product_description_lenght",
                "product_photos_qty",
            ])

        # Validation bronze
        df = validate_bronze(name, df)

        # Stockage
        out[name] = df

    return out


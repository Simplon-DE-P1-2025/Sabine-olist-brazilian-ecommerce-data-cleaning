# TRANSFORM (Silver)
from typing import Dict
import pandas as pd

def cast_basic_types(dfs: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
    """IDs -> string, dates -> datetime, amounts -> float (sans imputation)."""
    out = {k: v.copy() for k, v in dfs.items()}
    # TODO (Option A - étape 1) :
    # - IDs: astype("string")
    # - dates: pd.to_datetime(..., errors="coerce")
    # - montants: pd.to_numeric(..., errors="coerce")
    # - entiers: astype("Int64") quand utile
    return out

def add_quality_flags(dfs: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
    """Ajoute qc_* sur orders (sans modifier les valeurs)."""
    out = {k: v.copy() for k, v in dfs.items()}
    # TODO (Option A - étape 2) :
    # - qc_missing_delivered_customer_date
    # - qc_missing_carrier_date
    # - qc_missing_approved_at
    # - qc_temporal_inconsistency (checks chronologiques)
    return out

def geolocation_dedup(df_geo: pd.DataFrame) -> pd.DataFrame:
    """Dédoublonnage par (zip_prefix, city, state)."""
    # TODO (Option A - étape 3)
    return df_geo.copy()

def reviews_canonical(df_reviews: pd.DataFrame) -> pd.DataFrame:
    """Version canonique d'un avis : garder la plus récente par review_id."""
    # TODO (Option A - étape 4)
    return df_reviews.copy()

def build_silver(dfs_bronze: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
    dfs = cast_basic_types(dfs_bronze)
    dfs = add_quality_flags(dfs)
    if "geolocation" in dfs:
        dfs["geolocation_dedup"] = geolocation_dedup(dfs["geolocation"])
    if "order_reviews" in dfs:
        dfs["order_reviews_canon"] = reviews_canonical(dfs["order_reviews"])
    return dfs

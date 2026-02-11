# EXTRACT (Bronze)
from typing import Dict
import pandas as pd
from src.config import BRONZE_DIR

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

def read_csv_table(name: str) -> pd.DataFrame:
    if name not in REGISTRY:
        raise KeyError(f"Unknown table: {name}")
    path = BRONZE_DIR / REGISTRY[name]
    if not path.exists():
        raise FileNotFoundError(f"Missing file: {path}")
    return pd.read_csv(path)

def load_all() -> Dict[str, pd.DataFrame]:
    return {name: read_csv_table(name) for name in REGISTRY}
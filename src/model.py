# MODEL (Gold in-memory)
import pandas as pd

DATE_FMT = "%Y%m%d"  # 20180131

def dim_customers(df: pd.DataFrame) -> pd.DataFrame:
    # TODO (Option A - étape 5) : sélectionner colonnes et drop_duplicates("customer_id")
    return df.copy()

def dim_products(df: pd.DataFrame) -> pd.DataFrame:
    # TODO (Option A - étape 6) : colonnes produits utiles, drop_duplicates("product_id")
    return df.copy()

def dim_sellers(df: pd.DataFrame) -> pd.DataFrame:
    # TODO (Option A - étape 7) : colonnes vendeurs utiles, drop_duplicates("seller_id")
    return df.copy()

def dim_date_from_orders(df_orders: pd.DataFrame) -> pd.DataFrame:
    # TODO (Option A - étape 8) : collecter dates; fabriquer date_id (YYYYMMDD int)
    return pd.DataFrame(columns=["date_id","date","year","month","day"])

def fact_order_items(df_items: pd.DataFrame, df_orders: pd.DataFrame) -> pd.DataFrame:
    # TODO (Option A - étape 9) : joindre customer_id + date_id (yyyyMMdd) sur l'order_id
    return df_items.copy()

def build_gold(dfs_silver: dict) -> dict:
    dims = {
        "dim_customers": dim_customers(dfs_silver["customers"]),
        "dim_products":  dim_products(dfs_silver["products"]),
        "dim_sellers":   dim_sellers(dfs_silver["sellers"]),
        "dim_date":      dim_date_from_orders(dfs_silver["orders"]),
    }
    fact = {"fact_order_items": fact_order_items(dfs_silver["order_items"], dfs_silver["orders"])}
    return {**dims, **fact}
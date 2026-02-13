# ============================================================
# MODEL (Gold)
# ============================================================
#
# -- Construit les tables :
#       - dimensions, 
#       -  fact, 
#       - et auxiliaires (payments & order_reviews)

# -- Applique la validation Pandera Gold.
#
# ============================================================

from typing import Dict
import pandas as pd
import pandera.pandas as pa

from src.schemas.gold import (
    schema_dim_customers,
    schema_dim_products,
    schema_dim_sellers,
    schema_dim_date,
    schema_fact_orders,   
    schema_fact_order_items,
    schema_order_payments_gold,
    schema_order_reviews_gold,
)


# ---------- DIMENSIONS ----------

def dim_customers(df_customers: pd.DataFrame) -> pd.DataFrame:
    df = df_customers[["customer_id", "customer_city", "customer_state"]].drop_duplicates()
    return schema_dim_customers.validate(df)

def dim_products(df_products: pd.DataFrame) -> pd.DataFrame:
    df = df_products[[
        "product_id",
        "product_category_name",
        "product_category_name_english",
    ]].drop_duplicates()
    return schema_dim_products.validate(df)

def dim_sellers(df_sellers: pd.DataFrame) -> pd.DataFrame:
    df = df_sellers[[
        "seller_id",
        "seller_zip_code_prefix",
        "seller_city",
        "seller_state",
    ]].drop_duplicates()
    return schema_dim_sellers.validate(df)

def dim_date_from_orders(df_orders: pd.DataFrame) -> pd.DataFrame:
    df = pd.DataFrame()
    df["date"] = pd.to_datetime(df_orders["order_purchase_timestamp"].dropna().unique(), errors="coerce")
    df = df.dropna().reset_index(drop=True)

    df["year"]  = df["date"].dt.year
    df["month"] = df["date"].dt.month
    df["day"]   = df["date"].dt.day
    df["date_id"] = df["date"].dt.strftime("%Y%m%d").astype(int)

    df = df[df["date_id"].notna()]
    df = df.drop_duplicates(subset=["date_id"]).reset_index(drop=True)
    return schema_dim_date.validate(df)


# ---------- FACT TABLES ----------

def fact_orders(df_orders: pd.DataFrame) -> pd.DataFrame:
    df = df_orders[[
        "order_id",
        "customer_id",
        "order_status",
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ]].copy()

    df["purchase_date_id"] = (
        pd.to_datetime(df["order_purchase_timestamp"], errors="coerce")
          .dt.strftime("%Y%m%d")
          .astype("Int64")
    )

    return schema_fact_orders.validate(df)


def fact_order_items(df_items: pd.DataFrame, df_orders: pd.DataFrame) -> pd.DataFrame:
    df = df_items.merge(
        df_orders[["order_id", "customer_id", "order_purchase_timestamp"]],
        on="order_id",
        how="left"
    )

    df["purchase_date_id"] = (
        pd.to_datetime(df["order_purchase_timestamp"], errors="coerce")
          .dt.strftime("%Y%m%d")
          .astype("Int64")
    )

    df["shipping_limit_date_id"] = (
        pd.to_datetime(df["shipping_limit_date"], errors="coerce")
          .dt.strftime("%Y%m%d")
          .astype("Int64")
    )

    df = df.drop(columns=["order_purchase_timestamp"])

    return schema_fact_order_items.validate(df)


# ---------- TABLES AUXILIAIRES ----------

def table_order_payments(df_payments: pd.DataFrame) -> pd.DataFrame:
    return schema_order_payments_gold.validate(df_payments)

def table_order_reviews(df_reviews: pd.DataFrame) -> pd.DataFrame:
    cols = [
        "review_id", "order_id", "review_score",
        "review_creation_date", "review_answer_timestamp",
        "review_comment_title", "review_comment_message",
    ]
    df = df_reviews[[c for c in cols if c in df_reviews.columns]].copy()
    return schema_order_reviews_gold.validate(df)


# ---------- BUILD GOLD -----------

def build_gold(silver: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
    gold = {}

    gold["dim_customers"] = dim_customers(silver["customers"])
    gold["dim_products"]  = dim_products(silver["products"])
    gold["dim_sellers"]   = dim_sellers(silver["sellers"])

    # Fact header
    gold["fact_orders"] = fact_orders(silver["orders"])

    # Fact lines
    gold["fact_order_items"] = fact_order_items(
        silver["order_items"],
        silver["orders"]
    )

    # Dim date : union des dates réellement utilisées 
    date_ids = pd.concat([
        gold["fact_orders"]["purchase_date_id"],
        gold["fact_order_items"]["purchase_date_id"],
        gold["fact_order_items"]["shipping_limit_date_id"],
    ], ignore_index=True)

    # Dim_date depuis une série de date_id
    df_dates = pd.DataFrame({"date_id": date_ids.dropna().astype("Int64").unique()})
    df_dates["date"] = pd.to_datetime(df_dates["date_id"].astype(str), format="%Y%m%d", errors="coerce")
    df_dates = df_dates.dropna(subset=["date"]).drop_duplicates("date_id").sort_values("date_id").reset_index(drop=True)
    df_dates["year"] = df_dates["date"].dt.year.astype("Int64")
    df_dates["month"] = df_dates["date"].dt.month.astype("Int64")
    df_dates["day"] = df_dates["date"].dt.day.astype("Int64")
    gold["dim_date"] = schema_dim_date.validate(df_dates)

    # Auxiliaires
    gold["aux_order_payments"] = table_order_payments(silver["order_payments"])
    gold["aux_order_reviews"]  = table_order_reviews(silver["order_reviews"])

    return gold

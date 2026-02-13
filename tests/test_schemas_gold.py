import pandas as pd
import pandera.pandas as pa
from src.schemas.gold import (
    schema_dim_customers,
    schema_fact_order_items,
)

def test_dim_customers_unique_pk_ok():
    df = pd.DataFrame({
        "customer_id": ["c1", "c2"],
        "customer_city": ["Rennes", "Nantes"],
        "customer_state": ["RN", "NA"],
    })
    # Ne doit pas lever
    schema_dim_customers.validate(df)

def test_fact_order_items_requires_fk_columns():
    df = pd.DataFrame({
        "order_id": ["o1"],
        "order_item_id": [1],
        "product_id": ["p1"],
        "seller_id": ["s1"],
        "customer_id": ["c1"],                 # FK client exigée en Gold
        "shipping_limit_date": pd.to_datetime(["2017-01-06"]),
        "price": [10.0],
        "freight_value": [2.0],
        "date_id": [20170106],
    })
    schema_fact_order_items.validate(df)       # Ne doit pas lever

def test_fact_order_items_pk_composite_duplicate_raises():
    df_dup = pd.DataFrame({
        "order_id": ["o1", "o1"],
        "order_item_id": [1, 1],               # PK composite dupliquée
        "product_id": ["p1", "p1"],
        "seller_id": ["s1", "s1"],
        "customer_id": ["c1", "c1"],
        "shipping_limit_date": pd.to_datetime(["2017-01-06","2017-01-06"]),
        "price": [10.0, 10.0],
        "freight_value": [2.0, 2.0],
        "date_id": [20170106, 20170106],
    })
    import pytest
    with pytest.raises(pa.errors.SchemaError):
        schema_fact_order_items.validate(df_dup)
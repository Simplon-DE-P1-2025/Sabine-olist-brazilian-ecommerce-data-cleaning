import pandas as pd
from src.model import dim_customers, fact_order_items

def test_dim_customers_columns():
    df = pd.DataFrame({
        "customer_id": ["c1","c2"],
        "customer_city": ["X","Y"],
        "customer_state": ["SP","RJ"]
    })
    out = dim_customers(df)
    assert set(out.columns) == {"customer_id","customer_city","customer_state"}

def test_fact_contains_customer_id( ):
    items = pd.DataFrame({
        "order_id": ["o1"], "order_item_id": [1],
        "product_id": ["p1"], "seller_id": ["s1"],
        "shipping_limit_date": pd.to_datetime(["2017-01-06"])
    })
    orders = pd.DataFrame({
        "order_id": ["o1"], "customer_id": ["c1"],
        "order_purchase_timestamp": pd.to_datetime(["2017-01-01"])
    })
    out = fact_order_items(items, orders)
    assert "customer_id" in out.columns
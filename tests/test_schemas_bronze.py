import pandas as pd
from src.schemas.bronze import schema_orders_bronze

def test_orders_bronze_smoke_accepts_raw_like():
    df_raw_like = pd.DataFrame({
        "order_id": ["o1"],
        "customer_id": ["c1"],                 # types "object" tolérés
        "order_status": ["delivered"],
        "order_purchase_timestamp": ["2017-01-01 12:00:00"],
        "order_approved_at": [None],
        "order_delivered_carrier_date": [None],
        "order_delivered_customer_date": ["2017-01-05 15:30:00"],
        "order_estimated_delivery_date": ["2017-01-10 00:00:00"],
    })
    # Ne doit pas lever (Bronze est tolérant, coerce=False)
    schema_orders_bronze.validate(df_raw_like)
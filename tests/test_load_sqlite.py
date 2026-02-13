from src.load import apply_schema, load_tables, sanity_checks
import pandas as pd

def test_sanity_counts(tmp_path, monkeypatch):
    # Exemple minimal: fake tables à charger
    dfs = {
        "dim_customers": pd.DataFrame({"customer_id": ["c1"]}),
        "dim_products": pd.DataFrame({"product_id": ["p1"]}),
        "dim_sellers": pd.DataFrame({"seller_id": ["s1"]}),
        "dim_date": pd.DataFrame({"date_id": [20170106], "date": pd.to_datetime(["2017-01-06"]),
                                  "year":[2017], "month":[1], "day":[6]}),
        "fact_order_items": pd.DataFrame({
            "order_id":["o1"], "order_item_id":[1], "product_id":["p1"], "seller_id":["s1"],
            "customer_id":["c1"], "shipping_limit_date": pd.to_datetime(["2017-01-06"]),
            "price":[10.0], "freight_value":[2.0], "date_id":[20170106]
        }),
    }
    # Ici on ne reconfigure pas DB_PATH pour rester simple dans l’exemple.
    # (Si besoin, on peut monkeypatcher DB_PATH vers tmp_path / "olist.db")
    apply_schema()
    load_tables(dfs)
    rep = sanity_checks()
    assert rep.get("dim_customers_exists") is True
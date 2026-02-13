import pandas as pd
import pandera as pa
from src.schemas.silver import schema_order_reviews_silver

def test_schema_reviews_silver_ok():
    df = pd.DataFrame({
        "review_id": ["r1"],
        "order_id": ["o1"],
        "review_score": [5],
        "review_comment_title": [None],
        "review_comment_message": [None],
        "review_creation_date": ["2017-01-05"],
        "review_answer_timestamp": [None],
    })
    schema_order_reviews_silver.validate(df)  # ne doit pas lever

def test_schema_reviews_silver_invalid_score():
    df_bad = pd.DataFrame({
        "review_id": ["r1"],
        "order_id": ["o1"],
        "review_score": [8],  # hors [1,5]
        "review_creation_date": ["2017-01-05"],
        "review_answer_timestamp": [None],
    })
    import pytest
    with pytest.raises(pa.errors.SchemaError):
        schema_order_reviews_silver.validate(df_bad)
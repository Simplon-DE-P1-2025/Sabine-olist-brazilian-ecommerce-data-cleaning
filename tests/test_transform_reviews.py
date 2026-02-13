import pandas as pd
from src.transform import reviews_canonical

def test_reviews_canonical_basic():
    df = pd.DataFrame({
        "review_id": ["r1", "r1", "r2"],
        "review_creation_date": ["2017-01-01", "2017-01-05", "2017-02-01"],
        "review_score": [3, 5, 4],
    })
    out = reviews_canonical(df)
    assert len(out) == 2
    assert out.loc[out["review_id"] == "r1", "review_score"].iloc[0] == 5
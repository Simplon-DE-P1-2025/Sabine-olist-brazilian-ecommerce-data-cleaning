import pandas as pd
from src.transform import geolocation_dedup

def test_geolocation_dedup_basic():
    df = pd.DataFrame({
        "geolocation_zip_code_prefix": [12345, 12345, 54321],
        "geolocation_city": ["A", "A", "B"],
        "geolocation_state": ["SP", "SP", "RJ"],
        "geolocation_lat": [1.0, 1.0, 5.0],
        "geolocation_lng": [2.0, 2.0, 6.0],
    })
    out = geolocation_dedup(df)
    assert len(out) == 2
    assert set(out["geolocation_zip_code_prefix"]) == {12345, 54321}
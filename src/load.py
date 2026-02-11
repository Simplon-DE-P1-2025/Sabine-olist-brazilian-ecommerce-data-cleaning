# LOAD (Gold -> SQLite)
from pathlib import Path
import sqlite3
import pandas as pd
from src.config import DB_PATH, DDL_PATH

def apply_schema(ddl_path: Path = DDL_PATH, db_path: Path = DB_PATH) -> None:
    sql = Path(ddl_path).read_text(encoding="utf-8")
    with sqlite3.connect(db_path) as conn:
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.executescript(sql)

def load_tables(gold: dict, if_exists: str = "replace", db_path: Path = DB_PATH) -> None:
    with sqlite3.connect(db_path) as conn:
        conn.execute("PRAGMA foreign_keys = ON;")
        for t, df in gold.items():
            if isinstance(df, pd.DataFrame):
                df.to_sql(t, conn, if_exists=if_exists, index=False)

def sanity_checks(db_path: Path = DB_PATH) -> dict:
    report = {}
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        for t in ["dim_customers","dim_products","dim_sellers","dim_date","fact_order_items"]:
            try:
                cur.execute(f"SELECT COUNT(*) FROM {t};")
                report[f"count_{t}"] = cur.fetchone()[0]
            except sqlite3.Error:
                report[f"count_{t}"] = None
    return report
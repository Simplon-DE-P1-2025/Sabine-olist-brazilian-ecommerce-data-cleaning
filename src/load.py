# ============================================
# LOAD (Gold -> SQLite)
# ============================================
#
# -- Applique le DDL, charge les tables Gold, 
#   et effectue des sanity checks.
# 
# ============================================


import sqlite3
from pathlib import Path
from typing import Dict
import pandas as pd
import pandera.pandas as pa

from src.config import DB_PATH

def apply_schema(schema_path: Path = Path("sql/ddl/schema_etoile.sql")) -> None:
    """
    Applique le schéma SQL (DDL) pour recréer les tables Gold dans SQLite.
    """
    with sqlite3.connect(DB_PATH) as conn:
        with open(schema_path, "r", encoding="utf-8") as f:
            ddl = f.read()
        conn.executescript(ddl)

def load_tables(dfs: Dict[str, pd.DataFrame], if_exists: str = "replace") -> None:
    """
    Charge les DataFrames Gold dans la base SQLite selon l'ordre :
      1. Dims
      2. Fact
      3. Tables auxiliaires
    """
    order = [
    "dim_customers",
    "dim_products",
    "dim_sellers",
    "dim_date",
    "fact_orders",        
    "fact_order_items",
    "aux_order_payments",
    "aux_order_reviews",
]

    with sqlite3.connect(DB_PATH) as conn:
        for name in order:
            if name in dfs and isinstance(dfs[name], pd.DataFrame):
                dfs[name].to_sql(name, conn, if_exists=if_exists, index=False)

def sanity_checks() -> dict:
    """
    Contrôles simples :
      - existence des tables
      - nombre de lignes
    """
    checks = {}
    tables = [
    "dim_customers",
    "dim_products",
    "dim_sellers",
    "dim_date",
    "fact_orders",        
    "fact_order_items",
    "aux_order_payments",
    "aux_order_reviews",
]
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        for t in tables:
            cur.execute(
                "SELECT COUNT(*) FROM sqlite_master WHERE name=? AND type='table'",
                (t,)
            )
            exists = cur.fetchone()[0] == 1
            checks[f"{t}_exists"] = exists
            if exists:
                cur.execute(f"SELECT COUNT(*) FROM {t}")
                checks[f"{t}_rowcount"] = cur.fetchone()[0]
    return checks
from pathlib import Path

# Central config (Bronze -> Silver -> Gold)
BASE_DIR  = Path(__file__).resolve().parents[1]

DATA_DIR   = BASE_DIR / "data"
BRONZE_DIR = DATA_DIR / "bronze"
SILVER_DIR = DATA_DIR / "silver"
GOLD_DIR   = DATA_DIR / "gold"
DB_DIR     = DATA_DIR / "db"

DB_PATH  = DB_DIR / "olist.db"
DDL_PATH = BASE_DIR / "sql" / "ddl" / "schema_etoile.sql"

for d in (BRONZE_DIR, SILVER_DIR, GOLD_DIR, DB_DIR):
    d.mkdir(parents=True, exist_ok=True)
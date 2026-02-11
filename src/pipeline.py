# PIPELINE (Bronze -> Silver -> Gold)
import json
import pandas as pd
from pathlib import Path
from src import extract, transform, model, load
from src.config import SILVER_DIR, DB_PATH

def save_silver(dfs_silver: dict, out_dir: Path = SILVER_DIR) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, df in dfs_silver.items():
        if isinstance(df, pd.DataFrame):
            (out_dir / f"{name}.csv").write_text(df.to_csv(index=False), encoding="utf-8")

def run() -> dict:
    bronze = extract.load_all()
    silver = transform.build_silver(bronze)
    save_silver(silver)
    gold = model.build_gold(silver)
    load.apply_schema()
    load.load_tables(gold, if_exists="replace")
    return load.sanity_checks()

def main() -> None:
    rep = run()
    print(json.dumps(rep, indent=2, ensure_ascii=False))
    print(f"\nSQLite: {DB_PATH.resolve()}")

if __name__ == "__main__":
    main()
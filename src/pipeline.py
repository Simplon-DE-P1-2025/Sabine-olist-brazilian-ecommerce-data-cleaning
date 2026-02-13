# ======================================================
# Projet Olist — Pipeline BSG (Bronze → Silver → Gold)
# ======================================================
# Ce module fait partie du pipeline Data Engineering :
#
#   • Bronze : données brutes CSV (structure minimale validée)
#   • Silver : typage propre et transformations de qualité
#   • Gold   : modèle étoile + tables auxiliaires
#
# Les différentes étapes suivent une logique claire :
#   • extract.py   : chargement des fichiers Bronze + validation Bronze
#   • transform.py : construction Silver (typage + nettoyage + flags)
#   • model.py     : construction Gold (dims + fact + validations)
#   • load.py      : chargement SQLite (DDL + insert + checks)
#   • pipeline.py  : orchestration complète du flux
#
# Règles :
#   • Pandera assure la validation des données à chaque niveau.
#   • Les conversions manuelles sont interdites (coerce=True en Silver/Gold).
#   • Le code est modulaire, clair, testable et documenté.
#   • Le tout est conçu pour faciliter l’analyse SQL avancée.


# ======================================================
# PIPELINE (Orchestration : Bronze -> Silver -> Gold)
# ======================================================
import json
import pandera.pandas as pa
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
    # --- Bronze : extract + validation Bronze ---
    bronze = extract.load_all()

    # --- Silver ---
    silver = transform.build_silver(bronze)
    save_silver(silver)

    # --- Gold ---
    gold = model.build_gold(silver)

    # --- SQLite ---
    load.apply_schema()
    load.load_tables(gold, if_exists="replace")

    return load.sanity_checks()

def main() -> None:
    rep = run()
    print(json.dumps(rep, indent=2, ensure_ascii=False))
    print(f"\nSQLite: {DB_PATH.resolve()}")

if __name__ == "__main__":
    main()
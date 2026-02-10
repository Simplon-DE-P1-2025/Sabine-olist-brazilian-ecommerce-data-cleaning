# --- Imports ---
from __future__ import annotations

from pathlib import Path
import pandas as pd

# --- Constantes ---
RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")

# --- Fonctions utilitaires ---
def load_all_csv(raw_dir: Path) -> dict[str, pd.DataFrame]:
    """Load all CSV files from raw_dir into a dict of DataFrames."""
    csv_files = sorted(raw_dir.glob("*.csv"))
    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in {raw_dir.resolve()}")

    dfs: dict[str, pd.DataFrame] = {}
    for f in csv_files:
        name = f.stem.replace("olist_", "").replace("_dataset", "")
        dfs[name] = pd.read_csv(f)
    return dfs


def ensure_dirs() -> None:
    """Ensure output directories exist."""
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

# --- Typage des données [Cast_types()] ---
def cast_types(dfs: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    """Apply basic typing rules (ids as string, dates as datetime, amounts as float).
    No business logic, no imputations.
    """
    # --- IDs --> STRING ---
    id_columns = {
        "customers": ["customer_id", "customer_unique_id"],
        "orders": ["order_id", "customer_id"],
        "order_items": ["order_id", "product_id", "seller_id"],
        "order_payments": ["order_id"],
        "order_reviews": ["review_id", "order_id"],
        "products": ["product_id"],
        "sellers": ["seller_id"],
        # La géolocalisation n'a pas de clé primaire stable ; conservée en l'état pour l'instant.
        "product_category_name_translation": ["product_category_name"],
    }

    for table, cols in id_columns.items():
        if table in dfs:
            for col in cols:
                if col in dfs[table].columns:
                    dfs[table][col] = dfs[table][col].astype("string")

    # --- Dates --> DATETIME64[ns] (conversion des dates invalides en NaT) ---
    date_columns = {
        "orders": [
            "order_purchase_timestamp",
            "order_approved_at",
            "order_delivered_carrier_date",
            "order_delivered_customer_date",
            "order_estimated_delivery_date",
        ],
        "order_reviews": ["review_creation_date", "review_answer_timestamp"],
    }

    for table, cols in date_columns.items():
        if table in dfs:
            for col in cols:
                if col in dfs[table].columns:
                    dfs[table][col] = pd.to_datetime(dfs[table][col], errors="coerce")

    # --- Montants --> FLOAT ---
    amount_columns = {
        "order_items": ["price", "freight_value"],
        "order_payments": ["payment_value"],
    }

    for table, cols in amount_columns.items():
        if table in dfs:
            for col in cols:
                if col in dfs[table].columns:
                    dfs[table][col] = pd.to_numeric(dfs[table][col], errors="coerce")

    # --- Entiers (coercition sécurisée) ---
    if "order_items" in dfs and "order_item_id" in dfs["order_items"].columns:
        dfs["order_items"]["order_item_id"] = pd.to_numeric(
            dfs["order_items"]["order_item_id"], errors="coerce"
        ).astype("Int64")

    if "order_payments" in dfs and "payment_installments" in dfs["order_payments"].columns:
        dfs["order_payments"]["payment_installments"] = pd.to_numeric(
            dfs["order_payments"]["payment_installments"], errors="coerce"
        ).astype("Int64")

    return dfs

# --- Sauvegarde des tables dans data/processed ---
def save_processed_csv(dfs: dict[str, pd.DataFrame], out_dir: Path) -> None:
    """Save cleaned dataframes to out_dir as CSV (processed layer)."""
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, df in dfs.items():
        out_path = out_dir / f"{name}.csv"
        df.to_csv(out_path, index=False)


# --- Fonction principale ---
def main() -> None:
    # 1. Préparation
    ensure_dirs()
    dfs = load_all_csv(RAW_DIR)
    dfs = cast_types(dfs)

    # 2. Typage des données (IDs, dates, montants)
    dfs = cast_types(dfs)
# ============================================================================================
    # 3. FLAGS QUALITÉ (qc_*) (règles métier, AUCUNE correction)
    orders = dfs["orders"].copy()

    # Règle 2.1 — commande livrée sans date de livraison client
    orders["qc_missing_delivered_customer_date"] = (
        (orders["order_status"] == "delivered") &
        (orders["order_delivered_customer_date"].isna())
    )

    # Règle 2.1 — commande expédiée sans date transporteur
    carrier_required_statuses = {"shipped", "invoiced", "delivered"}
    orders["qc_missing_carrier_date"] = (
        orders["order_status"].isin(carrier_required_statuses) &
        (orders["order_delivered_carrier_date"].isna())
    )

    # Règle 2.2 — date d’approbation manquante (flag uniquement)
    orders["qc_missing_approved_at"] = orders["order_approved_at"].isna()

    # Règle 2.3 — incohérences temporelles (soft check)
    orders["qc_temporal_inconsistency"] = (
        (orders["order_approved_at"].notna() &
         (orders["order_approved_at"] < orders["order_purchase_timestamp"])) |
        (orders["order_delivered_carrier_date"].notna() &
         (orders["order_delivered_carrier_date"] < orders["order_purchase_timestamp"])) |
        (orders["order_delivered_customer_date"].notna() &
         (orders["order_delivered_customer_date"] < orders["order_purchase_timestamp"])) |
        (orders["order_delivered_customer_date"].notna() &
         orders["order_delivered_carrier_date"].notna() &
         (orders["order_delivered_customer_date"] < orders["order_delivered_carrier_date"])) |
        (orders["order_estimated_delivery_date"].notna() &
         orders["order_delivered_customer_date"].notna() &
         (orders["order_estimated_delivery_date"] < orders["order_delivered_customer_date"]))
    )

    dfs["orders"] = orders

# ===============================================================================================
    # 4. Comptage des NaT (diagnostic post-typage)
    date_cols_orders = [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ]

    print("\nNaT counts (orders):")
    nat_orders = dfs["orders"][date_cols_orders].isna().sum().sort_values(ascending=False)
    print(nat_orders)

    print("\nNaT rate % (orders):")
    print((nat_orders / len(dfs["orders"]) * 100).round(2))

# =============================================================================================
    # 5. Récapitulatif des flags qualité
    qc_cols = [
        "qc_missing_delivered_customer_date",
        "qc_missing_carrier_date",
        "qc_missing_approved_at",
        "qc_temporal_inconsistency",
    ]

    print("\nQC flag counts (orders):")
    print(dfs["orders"][qc_cols].sum().sort_values(ascending=False))

    print("\nQC flag rates % (orders):")
    print((dfs["orders"][qc_cols].mean() * 100).round(2))

# ============================================================================================
    # 6. Vérification finale (shapes)
    print("\nTables chargées :")
    for name, df in dfs.items():
        print(f"- {name}: shape={df.shape}")

# ============================================================================================
    # --- Comptage NaT sur les commandes ---
    date_cols_orders = [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ]

    print("\nNaT counts (orders):")
    nat_orders = dfs["orders"][date_cols_orders].isna().sum().sort_values(ascending=False)
    print(nat_orders)

    print("\nNaT rate % (orders):")
    nat_rate_orders = (nat_orders / len(dfs["orders"]) * 100).round(2)
    print(nat_rate_orders)

    # --- Comptage NaT sur les avis clients ---
    date_cols_reviews = ["review_creation_date", "review_answer_timestamp"]

    print("\nNaT counts (order_reviews):")
    nat_reviews = dfs["order_reviews"][date_cols_reviews].isna().sum().sort_values(ascending=False)
    print(nat_reviews)

    print("\nNaT rate % (order_reviews):")
    nat_rate_reviews = (nat_reviews / len(dfs["order_reviews"]) * 100).round(2)
    print(nat_rate_reviews)

    # --- Vérification typage (optionnel mais utile) ---
    print("\nType checks (orders):")
    print(dfs["orders"].dtypes)

    print("\nType checks (order_payments):")
    print(dfs["order_payments"].dtypes)

    # --- Affichage shapes ---
    print("\nLoaded tables:")
    for name, df in dfs.items():
        print(f"- {name}: shape={df.shape}")


    # 7. Sauvegarde des tables "processed"
    save_processed_csv(dfs, PROCESSED_DIR)
    print(f"\n✅ Tables sauvegardées dans : {PROCESSED_DIR.resolve()}")


# --- Point d’entrée du script ---
if __name__ == "__main__":
    main()
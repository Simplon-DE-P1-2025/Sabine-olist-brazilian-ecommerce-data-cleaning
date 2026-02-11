# Olist – de CSV bruts à base analytique 

Un README pour présenter un pipeline ETL simple et fiable, du dataset Olist jusqu’à une base analytique en étoile et des KPI métiers actionnables.

---

## 🎯 **Objectif :** transformer les CSV bruts Olist en une base SQLite modélisée en schéma en étoile pour répondre à des questions métier (ventes, logistique, satisfaction, paiements).

**Approche :** 3 étapes Exploration → Transformation/Chargement → Analyse ; nettoyage traçable, règles qualité explicites, zéro suppression destructive.

**Sorties :** tables propres, fact_order_items + dimensions, requêtes SQL KPI, et une narration claire pour comprendre le pourquoi derrière le comment.

---

## 1) Pourquoi ce projet ? 

Quand on ouvre pour la première fois les fichiers Olist, on voit des CSV hétérogènes, des dates parfois manquantes et des tables qui se répondent sans toujours s’aligner. Mon défi a été de rassembler, nettoyer et modéliser ces données de manière reproductible, puis d’en tirer des indicateurs métier qui aident à décider : où ça marche ? où ça coince ? et que peut-on améliorer ?

---

## 2) Le dataset en deux mots

Le projet s’appuie sur 9 fichiers décrivant l’écosystème e-commerce Olist (clients, commandes, articles, paiements, avis, produits, vendeurs, géolocalisation, traduction des catégories) sur la période 2016–2018. L’objectif est de passer d’un ensemble de fichiers plats à une base analytique interrogeable efficacement.

---

## 3) Ma stratégie d’analyse (les 4 piliers)

**Performance Commerciale** – comprendre l’évolution des ventes, la saisonnalité, les catégories et vendeurs qui tirent le chiffre d’affaires.

**Efficacité Logistique** – comparer délais réels vs estimés, repérer les États/régions en difficulté et la réactivité des vendeurs.

**Satisfaction Client** – analyser les review_score, les motifs d’insatisfaction (souvent liés à la livraison) et l’impact des retards sur les notes.

**Comportement d’Achat** – étudier les modes de paiement (carte, boleto…) et l’usage du paiement échelonné (ex. 6x, 10x) et son effet sur le panier moyen.

---

## 4) Architecture du pipeline (ETL)

Trois blocs simples, pensés pour une première itération reproductible :

- **01_exploration.ipynb** – audit de qualité : typage, valeurs manquantes, doublons, cohérence des clés et chronologie des dates.
- **02_pipeline.ipynb** – transformations : typage explicite (dates, numériques, identifiants), dédoublonnage de la géolocalisation, version canonique des avis (déduplication par review_id), chargement modélisé dans SQLite via SQLAlchemy.
- **03_requetes.ipynb** – requêtes d’analyse et KPI sur la base finale.

**Technos clés :** Python, pandas, SQLAlchemy, SQLite, notebooks Jupyter.

---

## 5) Règles de nettoyage & qualité (non destructives)

- **Dates manquantes = état métier** : on ne remplit pas artificiellement une livraison non encore effectuée ; on conserve NULL et on flague.
- **Intégrité référentielle** : vérification systématique des FK entre faits et dimensions.
- **Unicité** : contrainte d’unicité sur le couple (order_id, order_item_id) pour bannir les doublons techniques.
- **Chronologie (soft-checks)** : purchase ≤ approved ≤ delivered_carrier ≤ delivered_customer ≤ estimated_delivery ; en cas d’écart, on flague et on exclut des KPI de délais sans altérer la donnée brute.
- **Traçabilité** : colonnes *_missing, *_imputed, qc_* ; jobs idempotents (UPSERT/MERGE logiques).

---

## 6) Modélisation : schéma en étoile

La base `olist_final.sqlite` est structurée pour les requêtes analytiques rapides.

**Schéma visuel clair du pipeline (BSG)**
- Diagramme du pipeline Bronze → Silver → Gold (+ SQLite) 

flowchart LR
    subgraph Bronze
      A[data/bronze<br/>Raw CSVs] --> B["src/extract.py<br/>load_all()"]
    end

    subgraph Silver
      C["src/transform.py<br/>cast_basic_types()<br/>add_quality_flags()<br/>reviews_canonical()<br/>geolocation_dedup()"] --> D[data/silver<br/>Clean CSVs]
    end

    subgraph Gold
      E[src/model.py<br/>Dims + Fact] --> F["src/load.py<br/>apply_schema()<br/>load_tables()"]
      F --> G["data/db/olist.db<br/>SQLite (star schema)"]
    end

    B --> C
    D --> E

    H["[notebooks<br/>01_exploration<br/>02_etl<br/>03_analytics]"]


### Table de faits

**fact_order_items** — grain : 1 ligne = 1 produit vendu dans une commande.  
Mesures : price, freight_value (et métriques dérivées).

### Tables de dimensions

- dim_customers — localisation & identifiants clients
- dim_products — attributs produits & catégories
- dim_sellers — informations vendeurs
- dim_date — calendrier (jour, semaine, mois, trimestre, année)

       dim_date            dim_customers          dim_products         dim_sellers
           │                     │                       │                   │
           └──────────────┬──────┴──────────────┬────────┴───────────────┬───┘
                          ▼                     ▼                        ▼
                    fact_order_items (price, freight_value, …)


---

## 7) Des KPI… au service d’une histoire

Au-delà des chiffres, je raconte l’évolution de la marketplace :

- **Ventes & saisonnalité** : commandes par mois, CA mensuel, panier moyen ; où sont les pics ? qui les porte ?
- **Top performances** : top catégories et meilleurs vendeurs ; qui tire le marché ?
- **Logistique** : délai moyen de livraison, retard moyen et taux de retard ; quelles régions souffrent ?
- **Satisfaction** : distribution des review_score et impact des retards sur les notes ; où l’expérience casse ?
- **Paiement** : part des cartes vs boleto, usage du paiement en plusieurs fois et effet sur le panier moyen.

### Exemples de requêtes (extraits)

```sql
-- Commandes par mois
SELECT strftime('%Y-%m', o.order_purchase_timestamp) AS mois,
       COUNT(DISTINCT o.order_id) AS nb_commandes
FROM orders o
GROUP BY 1
ORDER BY 1;


-- Délai réel vs estimé (en jours)
SELECT c.customer_state AS etat,
       AVG(julianday(o.order_delivered_customer_date) - julianday(o.order_purchase_timestamp)) AS delai_reel_j,
       AVG(julianday(o.order_estimated_delivery_date) - julianday(o.order_purchase_timestamp)) AS delai_estime_j
FROM orders o
JOIN customers c ON c.customer_id = o.customer_id
WHERE o.order_delivered_customer_date IS NOT NULL
GROUP BY 1
ORDER BY 2 DESC;

8) Prise en main (exécution rapide)

# 1) Créer et activer un venv
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 2) Installer les dépendances minimales
pip install pandas sqlalchemy jupyter

# 3) Organiser les données
# data/raw/  -> CSV bruts Olist
# data/processed/ -> sorties nettoyées

# 4) Lancer les notebooks dans l’ordre
# 01_exploration.ipynb -> 02_pipeline.ipynb -> 03_requetes.ipynb


9) Structure du repository

olist-data-cleaning/
├── README.md
├── .gitignore
├── requirements.txt
├── data/
│   ├── raw/                 # CSV bruts (non versionnés)
│   └── processed/           # CSV nettoyés (non versionnés)
├── db/                      # SQLite (non versionné)
│   └── olist_final.sqlite
├── docs/
│   ├── README.md            # index documentation
│   ├── note_cadrage.md
│   ├── regles_nettoyage.md
│   ├── dictionnaire_data.md
│   └── schema_etoile.png
├── notebooks/
│   ├── 01_exploration.ipynb
│   ├── 02_pipeline.ipynb
│   └── 03_kpi.ipynb
├── sql/
│   ├── ddl/
│   │   └── schema_etoile.sql
│   ├── kpi/
│   │   ├── 01_commandes_mensuelles.sql
│   │   ├── 02_CA_mensuel.sql
│   │   ├── 03_panier_moyen.sql
│   │   ├── 04_top_categories.sql
│   │   ├── 05_top_vendeurs.sql
│   │   ├── 06_repartition_geographique_clients.sql
│   │   ├── 07_delai_moyen_livraison.sql
│   │   ├── 08_taux_livraisons_en_retard.sql
│   │   └── 09_retard_moyen_livraison.sql
│   └── checks/
│       ├── pk_uniqueness.sql
│       └── fk_integrity.sql
└── src/
    ├── __init__.py
    ├── config.py
    ├── db.py                # connexion SQLite/SQLAlchemy
    ├── etl/
    │   ├── extract.py        # lecture raw
    │   ├── transform.py      # typage + rules + qc flags
    │   └── load.py           # insert into SQLite
    └── quality/
        ├── checks.py         # contrôles PK/FK/temporal
        └── report.py         # résumé des qc flags



10) Limites & prochaines étapes

Étendre le modèle avec une fact_orders dédiée à la logistique
Enrichir la dimension produits
Ajouter des tests de données (Great Expectations / dbt tests)
Publier des dashboards BI
Automatiser via Airflow

11) Auteure

Projet pédagogique réalisé en mode data engineering : nettoyage → gouvernance → modélisation → KPI → storytelling.

— Sabine ANOKO
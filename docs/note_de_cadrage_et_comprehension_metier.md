# 🧭 Note de cadrage & compréhension métier
## Analyse de l’écosystème Olist (2016–2018)

---

## 1. Vision globale du projet

L'objectif de ce projet est de s'immerger dans les données d'Olist, la plus grande plateforme de vente en ligne du Brésil. Olist ne se contente pas de vendre des produits ; elle fait office de connecteur logistique entre des petites entreprises locales et les géants du e-commerce.

Ma mission consiste à transformer une base de données brute de 100 000 commandes en leviers de décision. Il s’agit de comprendre la dynamique entre les clients, les vendeurs et les transporteurs pour identifier les points de friction et les opportunités de croissance.

---

## 2. Architecture et granularité des données

Pour mener à bien cette analyse, j'ai utilisé les données issues de 9 fichiers distincts. Il était crucial de respecter la granularité de chaque table pour garantir la fiabilité de mes futurs calculs et éviter des erreurs de calcul (doublons) lors des jointures.

### Tables sources

| Table | Description | Granularité |
|------|------------|------------|
| olist_customers | Base client et localisation | 1 ligne = 1 client |
| olist_orders | Table pivot : statut et dates clés | 1 ligne = 1 commande |
| olist_order_items | Détails du panier (produit, vendeur, prix) | 1 ligne = 1 article par commande |
| olist_order_payments | Modalités de règlement | 1 ligne = 1 transaction |
| olist_order_reviews | Satisfaction et avis clients | 1 ligne = 1 avis |
| olist_products | Catalogue produits | 1 ligne = 1 produit |
| olist_sellers | Informations vendeurs | 1 ligne = 1 vendeur |
| olist_geolocation | Coordonnées géographiques | 1 ligne = 1 zone |
| product_category_name | Traduction des catégories | 1 ligne = 1 catégorie |

---

## 3. Flux de données & clés de liaison

La réussite de l'analyse repose sur la capacité à relier les données entre elles via des clés primaires (PK) et étrangères (FK).

### Relations principales

- **Orders ↔ Customers** : `customer_id`  
  → Un client unique possède un `customer_unique_id` constant mais un `customer_id` différent à chaque commande.

- **Orders ↔ Order_Items** : `order_id`  
  → Une commande peut contenir plusieurs articles.

- **Order_Items ↔ Products** : `product_id`

- **Order_Items ↔ Sellers** : `seller_id`

---

### Table centrale : Orders

La table **Orders** est le pivot du projet. Elle contient les jalons temporels critiques pour mesurer la performance :

- `order_purchase_timestamp` → date d'achat
- `order_delivered_customer_date` → date réelle de réception
- `order_estimated_delivery_date` → date estimée

**Note méthodologique :**  
Cette table permet de suivre le parcours temporel d'un achat, de la validation jusqu'à la livraison finale.

---

## 4. Problématiques métier & axes d’analyse

Imagine que tu entres dans l’écosystème Olist comme dans une grande marketplace bouillonnante.  
Des milliers de vendeurs, des millions de clients… mais derrière cette fluidité, des questions stratégiques émergent.

L’analyse s’articule autour de **quatre piliers**.

---

### 📈 Analyse commerciale & ventes

Comprendre le pouls du marché :

- Comment évoluent les ventes dans le temps ?
- Où sont les pics et les creux saisonniers ?
- Quelles catégories dominent ?
- Quels vendeurs génèrent le plus de chiffre d’affaires ?

Cette étape pose les fondations de la performance commerciale.

---

### 🚚 Efficacité logistique

La logistique est le cœur du modèle Olist :

- Les délais annoncés sont-ils respectés ?
- Existe-t-il des zones rouges logistiques ?
- Où se produit la friction dans le parcours client ?

Toute inefficacité logistique se reflète directement dans la satisfaction client.

---

### ⭐ Satisfaction client

Écouter la voix des clients :

- Score moyen de satisfaction
- Impact des retards sur les avis
- Catégories sujettes aux frustrations

Comprendre l’expérience réelle vécue.

---

### 💳 Comportement d’achat

Lire la psychologie des transactions :

- Modes de paiement dominants
- Paiement échelonné et panier moyen
- Différences géographiques de consommation

Le paiement raconte une histoire sur la confiance et le pouvoir d’achat.

---

## 🎯 Synthèse

Le projet s’articule autour de 4 piliers :

1. Performance commerciale
2. Efficacité logistique
3. Satisfaction client
4. Comportement d’achat

Ensemble, ils racontent l’histoire complète de la marketplace Olist :

🔍 où elle performe  
⚠️ où elle souffre  
🚀 où se trouvent les opportunités d’amélioration

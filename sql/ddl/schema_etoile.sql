-- ==========================================================
--  SCHEMA ETOILE OLIST — MODELE DATAWAREHOUSE (GOLD)
-- ==========================================================

DROP TABLE IF EXISTS fact_orders;
DROP TABLE IF EXISTS fact_order_items;
DROP TABLE IF EXISTS dim_customers;
DROP TABLE IF EXISTS dim_products;
DROP TABLE IF EXISTS dim_sellers;
DROP TABLE IF EXISTS dim_date;
DROP TABLE IF EXISTS aux_order_payments;
DROP TABLE IF EXISTS aux_order_reviews;

-- ============================
-- DIMENSIONS
-- ============================

CREATE TABLE dim_customers (
    customer_id TEXT PRIMARY KEY,
    customer_city TEXT,
    customer_state TEXT
);

CREATE TABLE dim_products (
    product_id TEXT PRIMARY KEY,
    product_category_name TEXT,
    product_category_name_english TEXT
);

CREATE TABLE dim_sellers (
    seller_id TEXT PRIMARY KEY,
    seller_zip_code_prefix INTEGER,
    seller_city TEXT,
    seller_state TEXT
);

CREATE TABLE dim_date (
    date_id INTEGER PRIMARY KEY,
    date TIMESTAMP,
    year INTEGER,
    month INTEGER,
    day INTEGER
);

-- ============================
-- FACT ORDERS (1 ligne par commande)
-- ============================
CREATE TABLE fact_orders (
    order_id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL,
    purchase_date_id INTEGER NOT NULL,
    order_status TEXT,
    order_purchase_timestamp TIMESTAMP,
    order_approved_at TIMESTAMP,
    order_delivered_carrier_date TIMESTAMP,
    order_delivered_customer_date TIMESTAMP,
    order_estimated_delivery_date TIMESTAMP,

    FOREIGN KEY(customer_id) REFERENCES dim_customers(customer_id),
    FOREIGN KEY(purchase_date_id) REFERENCES dim_date(date_id)
);

-- ============================
-- FACT ORDER ITEMS (lignes de commande)
-- ============================
CREATE TABLE fact_order_items (
    order_id TEXT NOT NULL,
    order_item_id INTEGER NOT NULL,
    product_id TEXT NOT NULL,
    seller_id TEXT NOT NULL,
    customer_id TEXT NOT NULL,
    shipping_limit_date TIMESTAMP,
    price REAL,
    freight_value REAL,

    purchase_date_id INTEGER NOT NULL,
    shipping_limit_date_id INTEGER,

    PRIMARY KEY(order_id, order_item_id),

    FOREIGN KEY(order_id) REFERENCES fact_orders(order_id),
    FOREIGN KEY(product_id) REFERENCES dim_products(product_id),
    FOREIGN KEY(seller_id) REFERENCES dim_sellers(seller_id),
    FOREIGN KEY(customer_id) REFERENCES dim_customers(customer_id),
    FOREIGN KEY(purchase_date_id) REFERENCES dim_date(date_id),
    FOREIGN KEY(shipping_limit_date_id) REFERENCES dim_date(date_id)
);

-- ============================
-- TABLE AUX PAYMENTS
-- ============================
CREATE TABLE aux_order_payments (
    order_id TEXT,
    payment_sequential INTEGER,
    payment_type TEXT,
    payment_installments INTEGER,
    payment_value REAL
);

-- ============================
-- TABLE AUX REVIEWS
-- ============================
CREATE TABLE aux_order_reviews (
    review_id TEXT PRIMARY KEY,
    order_id TEXT,
    review_score INTEGER,
    review_creation_date TIMESTAMP,
    review_answer_timestamp TIMESTAMP,
    review_comment_title TEXT,
    review_comment_message TEXT
);

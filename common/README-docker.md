
```
-- print all the tables
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;

select * from "product";


CREATE EXTENSION IF NOT EXISTS vector;

SELECT extname FROM pg_extension;

-- creating a vector table
CREATE TABLE vector_items (
  id SERIAL PRIMARY KEY,
  embedding vector(3)
);


select * from vector_items;


INSERT INTO vector_items (embedding) VALUES ('[1,2,3]'), ('[4,5,6]'), ('[1,1,1]');


SELECT * FROM vector_items ORDER BY embedding <-> '[2,3,4]' LIMIT 1;

SELECT * FROM vector_items ORDER BY embedding <=> '[2,3,4]' LIMIT 1;
```
-- Set up product collection data--
```
-- Table: public.collection

-- DROP TABLE IF EXISTS public.collection;

CREATE TABLE IF NOT EXISTS public.collection
(
    collection_id integer NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1 ),
    uuid uuid NOT NULL DEFAULT gen_random_uuid(),
    name character varying COLLATE pg_catalog."default" NOT NULL,
    description text COLLATE pg_catalog."default",
    code character varying COLLATE pg_catalog."default" NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT collection_pkey PRIMARY KEY (collection_id),
    CONSTRAINT "COLLECTION_CODE_UNIQUE" UNIQUE (code),
    CONSTRAINT "COLLECTION_UUID_UNIQUE" UNIQUE (uuid)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.collection
    OWNER to postgres;
```

-- Insert multiple records
```
INSERT INTO public.collection (
    name,
    description,
    code,
    created_at,
    updated_at
)
VALUES
    ('Electronics', 'All electronic items', 'COLL_ELEC', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Furniture', 'Various furniture items', 'COLL_FURN', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Books', 'Different genres of books', 'COLL_BOOK', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Clothing', 'Apparel and accessories', 'COLL_CLOTH', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);
  ```
  ---
  -- Create dummy product table
```  
-- Step 1: Drop the old table safely if it exists
DROP TABLE IF EXISTS public.g5_product CASCADE;

-- Step 2: Recreate the g5_product table with the updated schema
CREATE TABLE public.g5_product
(
    product_id integer NOT NULL GENERATED ALWAYS AS IDENTITY (
        INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1
    ),
    product_name text COLLATE pg_catalog."default" NOT NULL,
    product_description text COLLATE pg_catalog."default",
    product_stock_qty integer,
    currency character varying COLLATE pg_catalog."default",
    product_price numeric(12,4),
    collection_id integer,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT g5_product_pkey PRIMARY KEY (product_id),
    CONSTRAINT g5_product_collection_fkey FOREIGN KEY (collection_id)
        REFERENCES public.collection (collection_id)
        ON UPDATE CASCADE
        ON DELETE SET NULL,
    CONSTRAINT g5_product_name_collection_unique UNIQUE (product_name, collection_id)
)
TABLESPACE pg_default;
```
-- Insert dummy data--
INSERT INTO public.g5_product
    (product_name, product_description, product_stock_qty, currency, product_price, collection_id)
VALUES
-- =========================
-- Electronics (collection_id = 2)
-- =========================
('Samsung Galaxy M35 5G (6GB/128GB)',
 'Brand: Samsung | 6.6" sAMOLED, Exynos chipset, 50MP triple cam, 6000mAh',
 60, 'INR', 16999.00, 2),

('Redmi Buds 5 Pro TWS',
 'Brand: Xiaomi | ANC, dual drivers, up to 38h playtime, Bluetooth 5.3',
 120, 'INR', 3499.00, 2),

('boAt Airdopes 141 Neo',
 'Brand: boAt | 50ms low-latency gaming mode, ASAP™ Charge, IPX4',
 200, 'INR', 1299.00, 2),

('OnePlus Nord Power Bank 10000mAh',
 'Brand: OnePlus | 22.5W fast charge, dual USB output, slim design',
 150, 'INR', 1899.00, 2),

('LG 43" 4K UHD Smart TV (WebOS)',
 'Brand: LG | 43UR75 | 4K UHD, HDR10, AI Sound, popular OTT apps',
 35, 'INR', 32990.00, 2),

('Lenovo IdeaPad Slim 3 (Ryzen 5, 16GB/512GB)',
 'Brand: Lenovo | 15.6" FHD, Ryzen 5 5500U, Windows 11, MS Office',
 25, 'INR', 52990.00, 2),

-- =========================
-- Furniture (collection_id = 3)
-- =========================
('Nilkamal Astra Office Chair (Ergonomic)',
 'Brand: Nilkamal | Mesh back, lumbar support, adjustable height & tilt',
 40, 'INR', 7990.00, 3),

('Wakefit Andromeda Queen Bed (Engineered Wood)',
 'Brand: Wakefit | Queen size, storage drawers, walnut finish',
 18, 'INR', 21990.00, 3),

('Urban Ladder Calaba 6-Seater Dining Set',
 'Brand: Urban Ladder | Sheesham wood, natural finish, cushioned seats',
 10, 'INR', 28990.00, 3),

('Godrej Interio Nova 2-Door Wardrobe',
 'Brand: Godrej Interio | Engineered wood, shelves + hanging space, lockable',
 14, 'INR', 17990.00, 3),

('Home Centre Nxt Foldable Study Table',
 'Brand: Home Centre | Compact foldable desk, engineered wood, teak finish',
 30, 'INR', 5990.00, 3),

('Durian Marigold 3-Seater Sofa (Fabric)',
 'Brand: Durian | High-resilience foam, solid frame, grey upholstery',
 12, 'INR', 25990.00, 3),

-- =========================
-- Books (collection_id = 4)
-- =========================
('The Argumentative Indian',
 'Author: Amartya Sen | Publisher: Penguin Random House India | Non-fiction essays',
 120, 'INR', 599.00, 4),

('The White Tiger',
 'Author: Aravind Adiga | Publisher: HarperCollins India | Man Booker Prize winner',
 150, 'INR', 499.00, 4),

('India After Gandhi',
 'Author: Ramachandra Guha | Publisher: Picador India | Modern Indian history',
 90, 'INR', 799.00, 4),

('Atomic Habits',
 'Author: James Clear | Publisher: Penguin India | Self-improvement classic',
 200, 'INR', 699.00, 4),

('Ikigai: The Japanese Secret to a Long and Happy Life',
 'Authors: Héctor García, Francesc Miralles | Publisher: Penguin India | Lifestyle',
 170, 'INR', 499.00, 4),

('Better off being Indian',
 'Author: Asim Munir | Publisher: Radcliffe_Mountbatten | Historical fiction',
 110, 'INR', 399.00, 4),

-- =========================
-- Clothing (collection_id = 5)
-- =========================
('Allen Solly Men''s Slim Fit Cotton Shirt',
 'Brand: Allen Solly | Solid, full sleeve, office/formal wear',
 140, 'INR', 1999.00, 5),

('Fabindia Women''s Cotton Kurta (A-Line)',
 'Brand: Fabindia | Handblock print, 3/4 sleeve, festive/casual',
 95, 'INR', 2499.00, 5),

('Levi''s 511 Men''s Slim Fit Jeans',
 'Brand: Levi''s India | Stretch denim, mid-rise, classic 5-pocket',
 120, 'INR', 3499.00, 5),

('Biba Women''s Anarkali Kurta Set',
 'Brand: Biba | Printed kurta with dupatta, semi-stitched, occasion wear',
 60, 'INR', 3299.00, 5),

('Van Heusen Men''s Formal Trousers',
 'Brand: Van Heusen | Poly-viscose blend, wrinkle-resistant, flat-front',
 130, 'INR', 2499.00, 5),

('Puma Unisex Sports Jacket (Lightweight)',
 'Brand: Puma India | Zip-through, breathable, training/casual',
 80, 'INR', 2999.00, 5);

 --------------
 --Read sqls for product enquiry & collection enquiry - sample sqls---
 ```
 --1) “What items do you have on your collection?”
--A. List all collections (with basic info + product counts)
SELECT
  c.collection_id,
  c.name         AS collection_name,
  c.code         AS collection_code,
  COUNT(p.product_id) AS product_count
FROM public.collection c
LEFT JOIN public.g5_product p
  ON p.collection_id = c.collection_id
GROUP BY c.collection_id, c.name, c.code
ORDER BY c.collection_id;

--B. Show product names grouped under each collection (only in-stock)
SELECT
  c.collection_id,
  c.name AS collection_name,
  ARRAY_AGG(p.product_name ORDER BY p.product_name) FILTER (WHERE p.product_id IS NOT NULL) AS products_in_stock
FROM public.collection c
LEFT JOIN public.g5_product p
  ON p.collection_id = c.collection_id
  AND COALESCE(p.product_stock_qty, 0) > 0
GROUP BY c.collection_id, c.name
ORDER BY c.collection_id;

--C. Flat list of all products with their collection (easy to scan)
SELECT
  c.collection_id,
  c.name          AS collection_name,
  p.product_id,
  p.product_name,
  p.currency,
  p.product_price,
  p.product_stock_qty
FROM public.g5_product p
JOIN public.collection c
  ON c.collection_id = p.collection_id
ORDER BY c.collection_id, p.product_name;

--2) “Can you give me a catalogue of your products in each collection?”
--A. Catalogue table (one row per product, grouped by collection via ORDER)
SELECT
  c.collection_id,
  c.name          AS collection_name,
  p.product_id,
  p.product_name,
  p.product_description,
  p.currency,
  p.product_price,
  p.product_stock_qty
FROM public.g5_product p
JOIN public.collection c
  ON c.collection_id = p.collection_id
ORDER BY c.collection_id, p.product_name;

--B. JSON catalogue (one row per collection, products aggregated as JSON)
SELECT
  c.collection_id,
  c.name AS collection_name,
  JSONB_AGG(
    JSONB_BUILD_OBJECT(
      'product_id', p.product_id,
      'name',       p.product_name,
      'description',p.product_description,
      'currency',   p.currency,
      'price',      p.product_price,
      'stock_qty',  p.product_stock_qty
    )
    ORDER BY p.product_name
  ) AS products
FROM public.collection c
LEFT JOIN public.g5_product p
  ON p.collection_id = c.collection_id
GROUP BY c.collection_id, c.name
ORDER BY c.collection_id;

--C. CSV-friendly catalogue (formatted price, optional in-stock filter)
SELECT
  c.name AS collection,
  p.product_name AS product,
  p.product_description AS description,
  p.currency || ' ' || TO_CHAR(p.product_price, 'FM999,999,990.00') AS price,
  p.product_stock_qty AS stock
FROM public.g5_product p
JOIN public.collection c
  ON c.collection_id = p.collection_id
WHERE COALESCE(p.product_stock_qty, 0) > 0   -- remove this line if you want all
ORDER BY c.name, p.product_name;
```
--------
---ORDER
```
-- =========================
-- Orders
-- =========================
CREATE TABLE IF NOT EXISTS public.g5_order
(
    order_id integer NOT NULL GENERATED ALWAYS AS IDENTITY (
        INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1
    ),
    customer_name  text COLLATE pg_catalog."default" NOT NULL,
    customer_email text COLLATE pg_catalog."default" NOT NULL,
    customer_phone character varying(20),
    shipping_address text COLLATE pg_catalog."default" NOT NULL,
    shipping_notes   text COLLATE pg_catalog."default",
    currency character varying COLLATE pg_catalog."default" NOT NULL DEFAULT 'INR',
    total_price numeric(12,4) NOT NULL DEFAULT 0,  -- order total (see trigger/view below)
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT g5_order_pkey PRIMARY KEY (order_id),
    CONSTRAINT g5_order_email_check CHECK (position('@' in customer_email) > 1),
    CONSTRAINT g5_order_total_nonneg CHECK (total_price >= 0)
)
TABLESPACE pg_default;


-- =========================
-- Order Items
-- =========================
```
-- ===================================================================
-- DROP existing objects (order depends on items for CASCADE, so drop items first)
-- ===================================================================
DROP TABLE IF EXISTS public.g5_order_items CASCADE;
DROP TABLE IF EXISTS public.g5_order CASCADE;
DROP TYPE  IF EXISTS public.order_status_enum;

-- ===================================================================
-- Type: order_status_enum
-- Allowed values: received, processing, in transit, delivered, cancelled, returned
-- (Using a PostgreSQL ENUM for strict status control)
-- ===================================================================
CREATE TYPE public.order_status_enum AS ENUM (
  'received',
  'processing',
  'in transit',
  'delivered',
  'cancelled',
  'returned'
);

-- ===================================================================
-- Table: g5_order
-- ===================================================================
CREATE TABLE public.g5_order
(
    order_id integer NOT NULL GENERATED ALWAYS AS IDENTITY (
        INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1
    ),
    customer_name  text COLLATE pg_catalog."default" NOT NULL,
    customer_email text COLLATE pg_catalog."default" NOT NULL,
    customer_phone character varying(20),
    shipping_address text COLLATE pg_catalog."default" NOT NULL,
    shipping_notes   text COLLATE pg_catalog."default",
    currency character varying COLLATE pg_catalog."default" NOT NULL DEFAULT 'INR',
    payment_mode character varying COLLATE pg_catalog."default" NOT NULL DEFAULT 'COD',
    order_status public.order_status_enum NOT NULL DEFAULT 'received',
    total_price numeric(12,4) NOT NULL DEFAULT 0,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT g5_order_pkey PRIMARY KEY (order_id),
    CONSTRAINT g5_order_email_check CHECK (position('@' in customer_email) > 1),
    CONSTRAINT g5_order_total_nonneg CHECK (total_price >= 0)
)
TABLESPACE pg_default;

--INDEX
CREATE INDEX IF NOT EXISTS idx_g5_order_status ON public.g5_order(order_status);

-- ===================================================================
-- Table: g5_order_items
-- ===================================================================
--DROP TABLE IF EXISTS public.g5_order_items CASCADE;
--DROP TABLE IF EXISTS public.g5_order CASCADE;

CREATE TABLE public.g5_order_items
(
    order_item_id integer NOT NULL GENERATED ALWAYS AS IDENTITY (
        INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1
    ),
    order_id   integer NOT NULL,
    product_id integer NOT NULL,

    -- Snapshots for historical accuracy at purchase time
    product_name text COLLATE pg_catalog."default" NOT NULL,
    currency character varying COLLATE pg_catalog."default" NOT NULL,
    unit_price numeric(12,4) NOT NULL,
    quantity   integer NOT NULL,

    line_total numeric(12,4) GENERATED ALWAYS AS (unit_price * quantity) STORED,

    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT g5_order_items_pkey PRIMARY KEY (order_item_id),

    CONSTRAINT g5_order_items_order_fkey FOREIGN KEY (order_id)
        REFERENCES public.g5_order (order_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT g5_order_items_product_fkey FOREIGN KEY (product_id)
        REFERENCES public.g5_product (product_id)
        ON UPDATE CASCADE,

    CONSTRAINT g5_order_items_qty_check CHECK (quantity > 0),
    CONSTRAINT g5_order_items_price_nonneg CHECK (unit_price >= 0),

    -- One row per product per order (adjust if you need multiple lines per product, e.g., options)
    CONSTRAINT g5_order_items_unique_per_order UNIQUE (order_id, product_id)
)
TABLESPACE pg_default;

-- Helpful indexes
CREATE INDEX IF NOT EXISTS idx_g5_order_items_order_id   ON public.g5_order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_g5_order_items_product_id ON public.g5_order_items(product_id);

```

WITH orders_clean AS (
  SELECT
    c.customer_unique_id,
    o.order_purchase_timestamp::timestamp AS ts
  FROM olist_orders_dataset o
  JOIN olist_customers_dataset c ON o.customer_id = c.customer_id
  WHERE o.order_status != 'canceled'
),
kunjungan AS (
  SELECT DISTINCT
    customer_unique_id,
    DATE(ts) AS tanggal_kunjungan
  FROM orders_clean
),
kunjungan_diurutkan AS (
  SELECT
    customer_unique_id,
    tanggal_kunjungan,
    ROW_NUMBER() OVER (PARTITION BY customer_unique_id ORDER BY tanggal_kunjungan) AS urutan_kunjungan
  FROM kunjungan
),
kunjungan_12 AS (
  SELECT
    customer_unique_id,
    MAX(CASE WHEN urutan_kunjungan = 1 THEN tanggal_kunjungan END) AS kunjungan_1,
    MAX(CASE WHEN urutan_kunjungan = 2 THEN tanggal_kunjungan END) AS kunjungan_2
  FROM kunjungan_diurutkan
  WHERE urutan_kunjungan IN (1, 2)
  GROUP BY customer_unique_id
),
jeda AS (
  SELECT (kunjungan_2 - kunjungan_1) AS jeda_hari
  FROM kunjungan_12
  WHERE kunjungan_2 IS NOT NULL
)
SELECT
  ROUND(AVG(jeda_hari)::numeric, 1) AS rata_rata_jeda_hari,
  ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY jeda_hari)::numeric, 1) AS median_jeda_hari,
  MIN(jeda_hari) AS jeda_tercepat,
  MAX(jeda_hari) AS jeda_terlama
FROM jeda;
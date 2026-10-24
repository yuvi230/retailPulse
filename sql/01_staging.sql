-- 1. Row count and date range
SELECT COUNT(*) AS rows, MIN(invoice_date) AS first_date, MAX(invoice_date) AS last_date
FROM stg_online_retail;

-- 2. Rows per source sheet
SELECT source_sheet, COUNT(*) AS rows FROM stg_online_retail GROUP BY source_sheet;

-- 3. Cancellations
SELECT COUNT(*) AS cancelled_rows FROM stg_online_retail WHERE invoice LIKE 'C%';

-- 4. Missing customers
SELECT SUM(CASE WHEN customer_id IS NULL THEN 1 ELSE 0 END) AS null_customer_rows,
       ROUND(100.0 * SUM(CASE WHEN customer_id IS NULL THEN 1 ELSE 0 END) / COUNT(*), 2) AS pct
FROM stg_online_retail;

-- 5. Zero or negative prices
SELECT COUNT(*) AS bad_price_rows FROM stg_online_retail WHERE price <= 0;

-- 6. Negative quantity without a cancellation prefix (stock adjustments)
SELECT COUNT(*) AS adjustment_rows
FROM stg_online_retail WHERE quantity < 0 AND invoice NOT LIKE 'C%';

-- 7. Non-product stock codes
SELECT stock_code, COUNT(*) AS n FROM stg_online_retail
WHERE stock_code IN ('POST','D','M','BANK CHARGES','DOT','CRUK','AMAZONFEE','C2','S','B','ADJUST')
GROUP BY stock_code ORDER BY n DESC;

-- 8. Top countries
SELECT country, COUNT(*) AS rows FROM stg_online_retail
GROUP BY country ORDER BY rows DESC LIMIT 10;
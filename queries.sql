-- ================================================================================
-- E-COMMERCE MANAGEMENT DATABASE SYSTEM — 10 MANDATORY ANALYTICAL SQL QUERIES (a-j)
-- Course: CSE 303 Lab (Database Management System) — Summer 2026
-- Student ID: 22025214 | Section: 1-(3) | Independent University Bangladesh
-- Target DBMS: PostgreSQL 18.x (Neon PostgreSQL Cloud Engine)
-- ================================================================================

-- (a) Customer Profiles Directory:
-- Retrieve full_name, email, and membership_level for all registered customers.
SELECT full_name, email, membership_level 
FROM store_customer 
ORDER BY customer_id ASC;


-- (b) Product Details Catalog:
-- Retrieve name, brand, and price for all products in the catalog.
SELECT name, brand, price 
FROM store_product 
ORDER BY product_id ASC;


-- (c) Customer Name Search:
-- Retrieve email addresses of customers whose full name contains the substring 'man' (case-insensitive).
SELECT email 
FROM store_customer 
WHERE LOWER(full_name) LIKE '%man%';


-- (d) Order Summary Report:
-- Join ORDER and CUSTOMER tables to display order_id, customer full_name, order_date, and total_amount.
SELECT 
    o.order_id, 
    c.full_name AS customer_name, 
    o.order_date, 
    o.total_amount 
FROM store_order o
JOIN store_customer c ON o.customer_id = c.customer_id
ORDER BY o.order_id ASC;


-- (e) Above-Average Price Products:
-- Retrieve products whose unit price exceeds the overall average product price in the database.
SELECT product_id, name, price 
FROM store_product 
WHERE price > (SELECT AVG(price) FROM store_product)
ORDER BY price DESC;


-- (f) Category Inventory Count Aggregation:
-- Display total number of distinct products grouped by category name.
SELECT 
    c.name AS category_name, 
    COUNT(p.product_id) AS total_products 
FROM store_category c
LEFT JOIN store_product p ON c.category_id = p.category_id
GROUP BY c.category_id, c.name
ORDER BY total_products DESC;


-- (g) High-Value Product Categories:
-- Find categories where the average product price exceeds $5,000.
SELECT 
    c.name AS category_name, 
    ROUND(AVG(p.price), 2) AS average_price 
FROM store_category c
JOIN store_product p ON c.category_id = p.category_id
GROUP BY c.category_id, c.name
HAVING AVG(p.price) > 5000
ORDER BY average_price DESC;


-- (h) Warehouse Logistics Overview:
-- Retrieve warehouse name, physical location, and storage capacity for all logistics hubs.
SELECT warehouse_name, location, storage_capacity 
FROM store_warehouse 
ORDER BY warehouse_id ASC;


-- (i) Pending Orders Tracking:
-- Retrieve customer name and order date for all orders currently in 'Pending' status.
SELECT 
    c.full_name AS customer_name, 
    o.order_date 
FROM store_order o
JOIN store_customer c ON o.customer_id = c.customer_id
WHERE o.order_status = 'Pending'
ORDER BY o.order_date DESC;


-- (j) Customer Revenue & Lifetime Spend Summary:
-- Display total purchase amount spent by each customer across all completed orders.
SELECT 
    c.customer_id, 
    c.full_name, 
    COALESCE(SUM(o.total_amount), 0.00) AS total_spent 
FROM store_customer c
LEFT JOIN store_order o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.full_name
ORDER BY total_spent DESC;

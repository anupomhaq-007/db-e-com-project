-- ================================================================================
-- E-COMMERCE MANAGEMENT DATABASE SYSTEM — DDL SCHEMA & TRIGGERS
-- Course: CSE 303 Lab (Database Management System) — Summer 2026
-- Student ID: 22025214 | Section: 1-(3) | Independent University Bangladesh
-- Target DBMS: PostgreSQL 18.x (Neon PostgreSQL Cloud Engine)
-- ================================================================================

-- 1. CATEGORY TABLE
CREATE TABLE IF NOT EXISTS store_category (
    category_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT
);

-- 2. SUPPLIER TABLE
CREATE TABLE IF NOT EXISTS store_supplier (
    supplier_id SERIAL PRIMARY KEY,
    company_name VARCHAR(150) NOT NULL,
    contact_person VARCHAR(100),
    phone VARCHAR(20),
    email VARCHAR(100) UNIQUE,
    address TEXT
);

-- 3. PRODUCT TABLE (Faculty Product IDs 101 to 113)
CREATE TABLE IF NOT EXISTS store_product (
    product_id INT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    brand VARCHAR(100),
    price DECIMAL(10, 2) NOT NULL CHECK (price >= 0),
    stock_quantity INT NOT NULL DEFAULT 0 CHECK (stock_quantity >= 0),
    description TEXT,
    availability_status VARCHAR(20) DEFAULT 'In Stock',
    category_id INT REFERENCES store_category(category_id) ON DELETE SET NULL,
    supplier_id INT REFERENCES store_supplier(supplier_id) ON DELETE SET NULL
);

-- 4. CUSTOMER TABLE
CREATE TABLE IF NOT EXISTS store_customer (
    customer_id SERIAL PRIMARY KEY,
    user_id INT UNIQUE REFERENCES auth_user(id) ON DELETE CASCADE,
    full_name VARCHAR(150) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone VARCHAR(20),
    address TEXT,
    registration_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    membership_level VARCHAR(20) DEFAULT 'Regular'
);

-- 5. WAREHOUSE TABLE
CREATE TABLE IF NOT EXISTS store_warehouse (
    warehouse_id SERIAL PRIMARY KEY,
    warehouse_name VARCHAR(100) NOT NULL,
    location VARCHAR(200) NOT NULL,
    storage_capacity INT NOT NULL CHECK (storage_capacity > 0)
);

-- 6. WAREHOUSE_STOCK BRIDGE TABLE (Many-to-Many Bridge)
CREATE TABLE IF NOT EXISTS store_warehousestock (
    id SERIAL PRIMARY KEY,
    warehouse_id INT NOT NULL REFERENCES store_warehouse(warehouse_id) ON DELETE CASCADE,
    product_id INT NOT NULL REFERENCES store_product(product_id) ON DELETE CASCADE,
    stock_quantity INT NOT NULL DEFAULT 0 CHECK (stock_quantity >= 0),
    UNIQUE(warehouse_id, product_id)
);

-- 7. ORDER TABLE
CREATE TABLE IF NOT EXISTS store_order (
    order_id SERIAL PRIMARY KEY,
    customer_id INT NOT NULL REFERENCES store_customer(customer_id) ON DELETE CASCADE,
    order_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    order_status VARCHAR(20) DEFAULT 'Pending',
    shipping_address TEXT,
    total_amount DECIMAL(10, 2) DEFAULT 0.00 CHECK (total_amount >= 0)
);

-- 8. ORDER_DETAIL TABLE (Weak Entity)
CREATE TABLE IF NOT EXISTS store_orderdetail (
    detail_id SERIAL PRIMARY KEY,
    order_id INT NOT NULL REFERENCES store_order(order_id) ON DELETE CASCADE,
    product_id INT NOT NULL REFERENCES store_product(product_id) ON DELETE CASCADE,
    quantity INT NOT NULL CHECK (quantity > 0),
    unit_price DECIMAL(10, 2) NOT NULL CHECK (unit_price >= 0),
    subtotal DECIMAL(10, 2) NOT NULL CHECK (subtotal >= 0)
);

-- 9. PAYMENT TABLE (1:1 with Order)
CREATE TABLE IF NOT EXISTS store_payment (
    payment_id SERIAL PRIMARY KEY,
    order_id INT UNIQUE NOT NULL REFERENCES store_order(order_id) ON DELETE CASCADE,
    payment_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    amount DECIMAL(10, 2) NOT NULL CHECK (amount >= 0),
    tax DECIMAL(10, 2) DEFAULT 0.00 CHECK (tax >= 0),
    discount DECIMAL(10, 2) DEFAULT 0.00 CHECK (discount >= 0),
    final_amount DECIMAL(10, 2) NOT NULL CHECK (final_amount >= 0),
    payment_method VARCHAR(50) DEFAULT 'Credit Card',
    payment_status VARCHAR(20) DEFAULT 'Completed'
);

-- 10. ORDER_LOG TABLE (Audit Log for Trigger 3)
CREATE TABLE IF NOT EXISTS store_orderlog (
    log_id SERIAL PRIMARY KEY,
    order_id INT NOT NULL,
    deletion_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    details TEXT NOT NULL
);

-- ================================================================================
-- DATABASE TRIGGERS (Task-2 Triggers a, b, c)
-- ================================================================================

-- Trigger Function 1: Stock Validation Trigger
CREATE OR REPLACE FUNCTION check_product_stock_availability()
RETURNS TRIGGER AS $$
DECLARE
    current_stock INT;
BEGIN
    SELECT stock_quantity INTO current_stock FROM store_product WHERE product_id = NEW.product_id;
    IF NEW.quantity > current_stock THEN
        RAISE EXCEPTION 'Stock Exception: Requested quantity (%) exceeds available inventory (%) for Product ID %',
            NEW.quantity, current_stock, NEW.product_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_validate_stock ON store_orderdetail;
CREATE TRIGGER trigger_validate_stock
BEFORE INSERT ON store_orderdetail
FOR EACH ROW
EXECUTE FUNCTION check_product_stock_availability();


-- Trigger Function 2: Payment Final Amount Calculation Trigger
CREATE OR REPLACE FUNCTION calculate_payment_final_amount()
RETURNS TRIGGER AS $$
BEGIN
    NEW.final_amount := NEW.amount + COALESCE(NEW.tax, 0.00) - COALESCE(NEW.discount, 0.00);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_calculate_final_payment ON store_payment;
CREATE TRIGGER trigger_calculate_final_payment
BEFORE INSERT OR UPDATE ON store_payment
FOR EACH ROW
EXECUTE FUNCTION calculate_payment_final_amount();


-- Trigger Function 3: Order Deletion Audit Log Trigger
CREATE OR REPLACE FUNCTION log_deleted_order_audit()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO store_orderlog (order_id, deletion_timestamp, details)
    VALUES (
        OLD.order_id,
        CURRENT_TIMESTAMP,
        FORMAT('Deleted Order #%s placed on %s (Total: $%s)', OLD.order_id, OLD.order_date, OLD.total_amount)
    );
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_audit_order_deletion ON store_order;
CREATE TRIGGER trigger_audit_order_deletion
AFTER DELETE ON store_order
FOR EACH ROW
EXECUTE FUNCTION log_deleted_order_audit();

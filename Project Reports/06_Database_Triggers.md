# Database Triggers & Procedural Logic (PL/pgSQL)

## 1. Overview & Engine Architecture
Database triggers allow executing procedural logic directly within the PostgreSQL engine in response to Data Manipulation Language (DML) events (`INSERT`, `UPDATE`, `DELETE`).

Relying solely on application-level checks (e.g., Python code) can lead to data inconsistencies when multiple server workers execute concurrent requests. Database triggers enforce business rules consistently, regardless of how the database is accessed.

For Task 2 of the syllabus, we implemented **3 PL/pgSQL database triggers**:
1. **Stock Validation Trigger:** Prevents overselling item inventory.
2. **Automated Payment Calculation Trigger:** Enforces financial calculations for order payments.
3. **Order Deletion Audit Log Trigger:** Captures deleted order histories for compliance auditing.

---

## 2. Trigger 1: Stock Availability Validation

### 2.1 Problem Scenario
If two customers attempt to purchase the final unit of a product at the exact same millisecond, both application threads might read `stock_quantity = 1` and allow the transaction to proceed, resulting in a negative inventory balance (`stock_quantity = -1`).

### 2.2 PL/pgSQL Trigger Function Source Code

```sql
-- 1. Create procedural function
CREATE OR REPLACE FUNCTION check_product_stock_availability()
RETURNS TRIGGER AS $$
DECLARE
    available_stock INT;
    product_name VARCHAR(200);
BEGIN
    -- Query current stock and name for target product
    SELECT stock_quantity, name 
    INTO available_stock, product_name
    FROM store_product
    WHERE product_id = NEW.product_id;

    -- Stock check validation
    IF available_stock < NEW.quantity THEN
        RAISE EXCEPTION 'Insufficient Inventory Error: Product "%" (ID: %) only has % units remaining, but % were requested.',
            product_name, NEW.product_id, available_stock, NEW.quantity
            USING ERRCODE = 'P0001'; -- Custom user-defined exception code
    END IF;

    -- Automatically deduct stock if validation passes
    UPDATE store_product
    SET stock_quantity = stock_quantity - NEW.quantity
    WHERE product_id = NEW.product_id;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 2. Bind trigger to table event
DROP TRIGGER IF EXISTS trigger_validate_stock ON store_orderdetail;

CREATE TRIGGER trigger_validate_stock
BEFORE INSERT ON store_orderdetail
FOR EACH ROW
EXECUTE FUNCTION check_product_stock_availability();
```

### 2.3 Application Interception Handling
When PostgreSQL raises an exception (`RAISE EXCEPTION`), the database transaction rolls back automatically. The Django application catches the `django.db.DatabaseError` exception and alerts the user:

```python
try:
    OrderDetail.objects.create(order=order, product=product, quantity=requested_qty, unit_price=product.price)
except Exception as e:
    # Catches PL/pgSQL trigger exception P0001
    messages.error(request, f"Order Failed: {str(e)}")
    transaction.rollback()
```

---

## 3. Trigger 2: Automated Payment Calculation

### 3.1 Problem Scenario
Manual entry or client-side calculation of discounts and taxes can result in rounding mismatches between order subtotals and actual payments.

### 3.2 PL/pgSQL Trigger Function Source Code

```sql
-- 1. Create calculation trigger function
CREATE OR REPLACE FUNCTION calculate_payment_final_amount()
RETURNS TRIGGER AS $$
BEGIN
    -- Enforce equation: Final = Amount + Tax - Discount
    -- COALESCE handles null values by substituting 0.00
    NEW.final_amount := NEW.amount 
                        + COALESCE(NEW.tax, 0.00) 
                        - COALESCE(NEW.discount, 0.00);

    -- Enforce non-negative payment totals
    IF NEW.final_amount < 0.00 THEN
        NEW.final_amount := 0.00;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 2. Bind trigger to store_payment
DROP TRIGGER IF EXISTS trigger_calculate_payment ON store_payment;

CREATE TRIGGER trigger_calculate_payment
BEFORE INSERT OR UPDATE ON store_payment
FOR EACH ROW
EXECUTE FUNCTION calculate_payment_final_amount();
```

---

## 4. Trigger 3: Order Deletion Audit Logging

### 4.1 Problem Scenario
When an order is deleted (either accidentally or maliciously), auditing regulations require preserving a permanent record showing which order was deleted, its total value, and the precise timestamp of deletion.

### 4.2 PL/pgSQL Trigger Function Source Code

```sql
-- 1. Create audit function
CREATE OR REPLACE FUNCTION log_deleted_order_audit()
RETURNS TRIGGER AS $$
BEGIN
    -- Insert details of the OLD record into the store_orderlog table
    INSERT INTO store_orderlog (order_id, deletion_timestamp, details)
    VALUES (
        OLD.order_id,
        NOW(),
        CONCAT('AUDIT WARNING: Order #', OLD.order_id, 
               ' placed by Customer ID ', OLD.customer_id, 
               ' with Total Amount $', OLD.total_amount, 
               ' was permanently deleted from the active registry.')
    );

    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

-- 2. Bind trigger to AFTER DELETE event
DROP TRIGGER IF EXISTS trigger_audit_order_deletion ON store_order;

CREATE TRIGGER trigger_audit_order_deletion
AFTER DELETE ON store_order
FOR EACH ROW
EXECUTE FUNCTION log_deleted_order_audit();
```

---

## 5. Trigger Execution Lifecycle Summary

| Trigger Name | Event Binding | Execution Timing | Impact on Database Transaction |
| :--- | :--- | :--- | :--- |
| `trigger_validate_stock` | `INSERT` on `store_orderdetail` | `BEFORE` | Validates inventory and deducts stock count; aborts transaction if stock is insufficient. |
| `trigger_calculate_payment` | `INSERT / UPDATE` on `store_payment` | `BEFORE` | Calculates `final_amount = amount + tax - discount` prior to writing to disk. |
| `trigger_audit_order_deletion` | `DELETE` on `store_order` | `AFTER` | Writes a record to `store_orderlog` preserving historical audit data. |

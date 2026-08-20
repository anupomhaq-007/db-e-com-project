# Analytical SQL Queries & Database Intelligence

## 1. Overview & Objectives
Task 2 of the CSE 303 Lab curriculum mandates implementing **10 analytical database queries** to extract critical business metrics from raw transactional relational tables.

These queries cover fundamental SQL concepts including multi-table `INNER JOIN`s, `LEFT OUTER JOIN`s, scalar subqueries, aggregate functions (`COUNT`, `SUM`, `AVG`), `GROUP BY` clause grouping, `HAVING` clause post-aggregation filtering, pattern matching (`LIKE`), and `COALESCE` null-handling.

Below is the complete specification, SQL source code, Django ORM translation, execution analysis, and expected output tabular schemas for all 10 analytical queries.

---

## 2. Exhaustive Query Specifications (a through j)

### 2.1 Query (a): Customer Profile Directory
- **Business Question:** Retrieve a master list of all customer full names, email addresses, and membership tier allocations sorted sequentially by ID.
- **Raw ANSI SQL:**
  ```sql
  SELECT full_name, email, membership_level 
  FROM store_customer 
  ORDER BY customer_id ASC;
  ```
- **Django ORM Equivalent:**
  ```python
  Customer.objects.all().order_by('customer_id').values('full_name', 'email', 'membership_level')
  ```
- **Technical Analysis:** Performs a sequential index scan over the `store_customer` primary key index.
- **Sample Result Output:**

| Full Name | Email | Membership Level |
| :--- | :--- | :--- |
| Asiful Islam | asiful@iub.edu.bd | Premium |
| Sakib Mohammad Ome | sakib@iub.edu.bd | Regular |
| Shadman Samin Shahriar | shadman@iub.edu.bd | VIP |

---

### 2.2 Query (b): Public Product Catalog
- **Business Question:** Extract all available product names, brands, and selling prices for public display.
- **Raw ANSI SQL:**
  ```sql
  SELECT name, brand, price 
  FROM store_product 
  ORDER BY product_id ASC;
  ```
- **Django ORM Equivalent:**
  ```python
  Product.objects.all().order_by('product_id').values('name', 'brand', 'price')
  ```
- **Sample Result Output:**

| Name | Brand | Price ($) |
| :--- | :--- | :--- |
| Gaming Laptop X1 | Asus | 1499.99 |
| Wireless Mouse M3 | Logitech | 29.99 |
| Mechanical Keyboard K2 | Keychron | 89.99 |

---

### 2.3 Query (c): Customer Substring Search (Pattern Matching)
- **Business Question:** Locate email addresses of all customers whose name contains the substring `'man'` (case-insensitive search).
- **Raw ANSI SQL:**
  ```sql
  SELECT email 
  FROM store_customer 
  WHERE LOWER(full_name) LIKE '%man%';
  ```
- **Django ORM Equivalent:**
  ```python
  Customer.objects.filter(full_name__icontains='man').values_list('email', flat=True)
  ```
- **Technical Analysis:** Utilizes `LOWER()` function and wildcard `%` match to guarantee case-insensitive pattern matching across customer records.
- **Sample Result Output:**

| Email |
| :--- |
| sakib@iub.edu.bd |
| shadman@iub.edu.bd |

---

### 2.4 Query (d): Customer Order Summary JOIN
- **Business Question:** Generate an executive order log linking each order ID, customer name, date, and total dollar amount.
- **Raw ANSI SQL:**
  ```sql
  SELECT o.order_id, c.full_name AS customer_name, o.order_date, o.total_amount 
  FROM store_order o 
  INNER JOIN store_customer c ON o.customer_id = c.customer_id 
  ORDER BY o.order_id ASC;
  ```
- **Django ORM Equivalent:**
  ```python
  Order.objects.select_related('customer').values('order_id', 'customer__full_name', 'order_date', 'total_amount')
  ```
- **Technical Analysis:** Executes an `INNER JOIN` over the primary key / foreign key relationship `store_order.customer_id = store_customer.customer_id`.
- **Sample Result Output:**

| Order ID | Customer Name | Order Date | Total Amount ($) |
| :--- | :--- | :--- | :--- |
| 5001 | Asiful Islam | 2026-08-01 10:30:00 | 1529.98 |
| 5002 | Shadman Samin | 2026-08-03 14:15:00 | 89.99 |

---

### 2.5 Query (e): Premium Products Above Average Price
- **Business Question:** Identify all luxury items priced higher than the average catalog price across the entire system.
- **Raw ANSI SQL:**
  ```sql
  SELECT product_id, name, price 
  FROM store_product 
  WHERE price > (SELECT AVG(price) FROM store_product) 
  ORDER BY price DESC;
  ```
- **Django ORM Equivalent:**
  ```python
  avg_price = Product.objects.aggregate(Avg('price'))['price__avg']
  Product.objects.filter(price__gt=avg_price).values('product_id', 'name', 'price')
  ```
- **Technical Analysis:** Evaluates a nested scalar subquery `(SELECT AVG(price) FROM store_product)` first, returning a constant threshold against which outer row prices are filtered.
- **Sample Result Output:**

| Product ID | Name | Price ($) |
| :--- | :--- | :--- |
| 101 | Gaming Laptop X1 | 1499.99 |
| 104 | UltraWide Monitor 34" | 799.99 |

---

### 2.6 Query (f): Product Distribution by Category
- **Business Question:** Count the total number of products assigned to each category, including categories with zero products.
- **Raw ANSI SQL:**
  ```sql
  SELECT c.name AS category_name, COUNT(p.product_id) AS total_products 
  FROM store_category c 
  LEFT OUTER JOIN store_product p ON c.category_id = p.category_id 
  GROUP BY c.category_id, c.name 
  ORDER BY total_products DESC;
  ```
- **Django ORM Equivalent:**
  ```python
  Category.objects.annotate(total_products=Count('product')).values('name', 'total_products')
  ```
- **Technical Analysis:** Utilizes a `LEFT OUTER JOIN` to preserve empty categories in the aggregation set and `COUNT(p.product_id)` to ignore null foreign key references.
- **Sample Result Output:**

| Category Name | Total Products |
| :--- | :--- |
| Electronics | 5 |
| Peripherals | 4 |
| Accessories | 0 |

---

### 2.7 Query (g): High-Value Category Filter (HAVING Clause)
- **Business Question:** Identify categories whose average product price exceeds $500.00.
- **Raw ANSI SQL:**
  ```sql
  SELECT c.name AS category_name, ROUND(AVG(p.price), 2) AS average_price 
  FROM store_category c 
  INNER JOIN store_product p ON c.category_id = p.category_id 
  GROUP BY c.category_id, c.name 
  HAVING AVG(p.price) > 500.00;
  ```
- **Django ORM Equivalent:**
  ```python
  Category.objects.annotate(avg_price=Avg('product__price')).filter(avg_price__gt=500.00).values('name', 'avg_price')
  ```
- **Technical Analysis:** Illustrates the distinction between `WHERE` (pre-aggregation filter) and `HAVING` (post-aggregation group filter).
- **Sample Result Output:**

| Category Name | Average Price ($) |
| :--- | :--- |
| Electronics | 1149.99 |

---

### 2.8 Query (h): Warehouse Capacity Overview
- **Business Question:** Retrieve physical warehouse names, locations, and total storage capacities.
- **Raw ANSI SQL:**
  ```sql
  SELECT warehouse_name, location, storage_capacity 
  FROM store_warehouse 
  ORDER BY storage_capacity DESC;
  ```
- **Django ORM Equivalent:**
  ```python
  Warehouse.objects.all().order_by('-storage_capacity').values('warehouse_name', 'location', 'storage_capacity')
  ```
- **Sample Result Output:**

| Warehouse Name | Location | Storage Capacity (Units) |
| :--- | :--- | :--- |
| Central Distribution Hub | Dhaka | 50000 |
| North Regional Hub | Chittagong | 25000 |

---

### 2.9 Query (i): Pending Orders Tracking
- **Business Question:** Find all orders currently in `'Pending'` status alongside the associated customer names for logistics fulfillment.
- **Raw ANSI SQL:**
  ```sql
  SELECT o.order_id, c.full_name AS customer_name, o.order_date, o.order_status 
  FROM store_order o 
  INNER JOIN store_customer c ON o.customer_id = c.customer_id 
  WHERE o.order_status = 'Pending';
  ```
- **Django ORM Equivalent:**
  ```python
  Order.objects.filter(order_status='Pending').select_related('customer').values('order_id', 'customer__full_name', 'order_date')
  ```
- **Sample Result Output:**

| Order ID | Customer Name | Order Date | Order Status |
| :--- | :--- | :--- | :--- |
| 5003 | Sakib Mohammad Ome | 2026-08-10 16:45:00 | Pending |

---

### 2.10 Query (j): Customer Lifetime Value & Revenue Report
- **Business Question:** Calculate total cumulative spending for every customer in the database, substituting `$0.00` for customers with no order history.
- **Raw ANSI SQL:**
  ```sql
  SELECT c.customer_id, c.full_name, COALESCE(SUM(o.total_amount), 0.00) AS total_spent 
  FROM store_customer c 
  LEFT OUTER JOIN store_order o ON c.customer_id = o.customer_id 
  GROUP BY c.customer_id, c.full_name 
  ORDER BY total_spent DESC;
  ```
- **Django ORM Equivalent:**
  ```python
  Customer.objects.annotate(
      total_spent=Coalesce(Sum('order__total_amount'), Value(0.00))
  ).values('customer_id', 'full_name', 'total_spent').order_by('-total_spent')
  ```
- **Technical Analysis:** `COALESCE(SUM(...), 0.00)` replaces SQL `NULL` results (produced when a customer has no matching `LEFT JOIN` rows in `store_order`) with `0.00`, ensuring accurate financial output.
- **Sample Result Output:**

| Customer ID | Full Name | Total Spent ($) |
| :--- | :--- | :--- |
| 1 | Asiful Islam | 1529.98 |
| 3 | Shadman Samin | 89.99 |
| 2 | Sakib Mohammad Ome | 0.00 |
| 4 | New Customer | 0.00 |

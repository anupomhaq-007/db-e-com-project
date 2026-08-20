# E-Commerce Management Database System
**Comprehensive Mini Project Report**

**Course:** CSE 303 Lab - Database Management (Summer 2026)  
**Institution:** Independent University, Bangladesh (IUB)  

**Prepared By:**
- Asiful Islam (ID: 2420197, Section: 5)
- Sakib Mohammad Ome (ID: 2220867, Section: 4)
- Shadman Samin Shahriar (ID: 2211120, Section: 2)

---

## 1. Introduction and System Overview
The objective of this mini-project was to design, implement, and deploy a fully functional E-Commerce Database System, translating theoretical database management concepts into a practical, real-world software architecture. 

Instead of relying merely on standalone SQL scripts, we integrated our database with a robust Django 5.2 backend and a responsive HTML5/Bootstrap 5 frontend. The database engine driving the application is a cloud-hosted Neon PostgreSQL 18.x instance. By strictly adhering to the requirements set forth in the CSE 303 Lab syllabus, we successfully implemented a cohesive platform that seamlessly manages inventory, users, financial transactions, and complex analytical reporting.

This document details every phase of the project's lifecycle, from conceptual entity-relationship modeling and rigorous normalization to advanced SQL triggers, RAID storage simulations, and B+ Tree indexing.

---

## 2. Database Design & Architecture (Task 1)

Our first major milestone was establishing a robust Entity-Relationship (ER) model. The design strictly adhered to relational database principles, utilizing Crow's Foot notation to represent relationships, cardinalities, and entity dependencies.

### 2.1 Core Entities and Attributes
We identified and designed 10 core tables to capture the operational reality of an e-commerce platform:

1. **Category (`store_category`):** Manages product classifications. Attributes: `category_id` (PK), `name` (Unique), `description`.
2. **Supplier (`store_supplier`):** Tracks vendor information. Attributes: `supplier_id` (PK), `company_name`, `contact_person`, `phone`, `email` (Unique), `address`.
3. **Product (`store_product`):** The central inventory catalog, seeded with faculty-mandated Product IDs (101 to 113). Attributes: `product_id` (PK), `name`, `brand`, `price` (CHECK >= 0), `stock_quantity`, `description`, `availability_status`. Includes Foreign Keys to Category and Supplier.
4. **Customer (`store_customer`):** Stores user profiles. Attributes: `customer_id` (PK), `user_id` (FK to Auth), `full_name`, `email`, `phone`, `address`, `registration_date`, `membership_level`.
5. **Warehouse (`store_warehouse`):** Tracks physical logistics hubs. Attributes: `warehouse_id` (PK), `warehouse_name`, `location`, `storage_capacity`.
6. **Order (`store_order`):** Represents customer transactions. Attributes: `order_id` (PK), `customer_id` (FK), `order_date`, `order_status`, `shipping_address`, `total_amount`.
7. **Order Detail (`store_orderdetail`):** A **Weak Entity** resolving the many-to-many relationship between Orders and Products. Attributes: `detail_id` (PK), `order_id` (FK), `product_id` (FK), `quantity`, `unit_price`, `subtotal`.
8. **Payment (`store_payment`):** Maintains a strictly **1:1 Relationship** with Orders. Attributes: `payment_id` (PK), `order_id` (Unique FK), `payment_date`, `amount`, `tax`, `discount`, `final_amount`, `payment_method`, `payment_status`.
9. **Warehouse Stock (`store_warehousestock`):** A **Bridge Table** to resolve the Many-to-Many relationship between Warehouses and Products. Ensures we can track exactly how much of a specific product is in a specific warehouse.
10. **Order Log (`store_orderlog`):** An audit table utilized exclusively by our database triggers to record deleted orders.

### 2.2 Structural Corrections and Improvements
During the conceptualization phase, we refined the initial ER diagram to resolve structural flaws:
- We merged duplicate Customer tables into a single canonical entity.
- We eliminated invalid direct links between the Order Log and Warehouse entities, as the audit log should strictly track order records.
- We implemented bridge tables to properly satisfy Third Normal Form (3NF) requirements.

---

## 3. SQL Implementation and Analytical Queries (Task 2)

Following the ER design, we generated the DDL (Data Definition Language) schema. We utilized PostgreSQL `SERIAL` types for auto-incrementing primary keys and enforced strict data integrity using `ON DELETE CASCADE` and `ON DELETE SET NULL` constraints.

We then developed 10 mandatory analytical queries to extract actionable business intelligence from the dataset:

- **(a) Customer Profiles:** `SELECT full_name, email, membership_level FROM store_customer ORDER BY customer_id ASC;`
- **(b) Product Details:** Retrieved the catalog showing `name`, `brand`, and `price`.
- **(c) Pattern Matching (Customer Search):** Used `WHERE LOWER(full_name) LIKE '%man%'` to identify specific users dynamically.
- **(d) Order Summary (JOIN):** Joined `store_order` and `store_customer` to map order IDs to human-readable customer names alongside total amounts.
- **(e) Subqueries (Above-Average Price):** Filtered products using a subquery: `WHERE price > (SELECT AVG(price) FROM store_product)`.
- **(f) Aggregation (Category Inventory):** Used `LEFT JOIN` and `COUNT(product_id)` grouped by category to show total item counts per classification.
- **(g) Advanced Filtering (High-Value Categories):** Used `GROUP BY` and `HAVING AVG(p.price) > 5000` to find premium categories.
- **(h) Logistics Overview:** Displayed standard warehouse operational metrics.
- **(i) Status Tracking:** Filtered orders `WHERE order_status = 'Pending'`.
- **(j) Customer Lifetime Value:** Used `COALESCE(SUM(o.total_amount), 0.00)` grouped by customer to calculate total historical spend per user.

---

## 4. Advanced Database Triggers (Task 2)

To ensure data integrity at the database engine level (preventing application-layer race conditions), we programmed three PL/pgSQL Trigger Functions:

1. **Stock Validation Trigger (`check_product_stock_availability`):**
   Fires `BEFORE INSERT` on `store_orderdetail`. It checks the requested `NEW.quantity` against the current `stock_quantity` in `store_product`. If the requested amount exceeds available stock, it throws an exception (`RAISE EXCEPTION`), aborting the transaction and preventing overselling.

2. **Automated Payment Calculation Trigger (`calculate_payment_final_amount`):**
   Fires `BEFORE INSERT OR UPDATE` on `store_payment`. It intercepts the record and automatically computes `NEW.final_amount := NEW.amount + COALESCE(NEW.tax, 0.00) - COALESCE(NEW.discount, 0.00)`. This guarantees mathematical consistency for financial records.

3. **Order Deletion Audit Log Trigger (`log_deleted_order_audit`):**
   Fires `AFTER DELETE` on `store_order`. It captures the `OLD.order_id` and formats a detailed text string containing the deleted total amount and date, inserting it into the `store_orderlog` table. This provides a secure, tamper-proof audit trail for destructive actions.

---

## 5. Scenario-Based Database Recovery — RAID Level 4 (Task 3)

Data loss prevention was addressed through a RAID 4 storage simulation. We designed an architecture featuring 6 Data Disks (D1 through D6) and 1 dedicated Parity Disk (P).

**The Configuration:**
We used 4-bit data blocks representing core tables:
- D1 (Product): `1010`
- D2 (Category): `1100`
- D3 (Customer): `0111`
- D4 (Supplier): `1001`
- D5 (Order): `0011`
- D6 (Payment): `1110`

**Parity Calculation:**
Parity (P) is calculated using a bitwise XOR (⊕) operation across all data disks:
`P = D1 ⊕ D2 ⊕ D3 ⊕ D4 ⊕ D5 ⊕ D6 = 0101`

**Recovery Simulation:**
If disk D5 suffers a catastrophic hardware failure, the system automatically reconstructs the lost block by XORing the surviving data disks against the Parity disk:
`Recovered D5 = D1 ⊕ D2 ⊕ D3 ⊕ D4 ⊕ D6 ⊕ P = 0011`
The reconstructed data matches the original block perfectly, demonstrating fault tolerance.

---

## 6. Database Normalization (Task 4)

To prevent data anomalies, our schema was mathematically normalized. We walked an unnormalized sample table (containing orders with multiple repeating product rows) through three distinct phases:

- **First Normal Form (1NF):** We flattened the structure, ensuring every cell contained only a single, atomic value (no comma-separated lists of products).
- **Second Normal Form (2NF):** We identified a composite primary key (Order ID + Product ID). We removed partial dependencies by separating order-specific data (Order Date, Customer ID) from product-specific data (Product Name, Unit Price).
- **Third Normal Form (3NF):** We eliminated transitive dependencies. For example, Customer Name depends on Customer ID, not Order ID. We extracted Customer Name into a distinct Customer table, resulting in a perfectly normalized relational structure.

---

## 7. Hashing, Indexing & B+ Trees (Task 5)

To optimize search times for the `store_product` catalog, we implemented B+ Tree indexing. Unlike standard B-Trees, B+ Trees store all actual data pointers exclusively in the leaf nodes, which are linked as a linked-list, making range queries incredibly fast.

**Tree Characteristics:**
- **Index Key:** `Product_ID`
- **Order:** 3 (maximum of 3 keys per node, minimum of 1).
- **Insertion Sequence:** `110, 104, 101, 113, 107, 109, 102, 111, 105, 108, 103, 112, 106`

**Simulated Operations:**
- **Search (108):** Starting at the root, the search compares 108 against the internal node split values, navigating left or right down the tree in logarithmic time `O(log n)` until it reaches the leaf node containing 108.
- **Deletion (105):** When deleting key 105, the leaf node underflows (drops below the minimum key count). The tree automatically borrows a key from a sibling node and updates the internal routing nodes to maintain perfect balance.

---

## 8. Web Application Integration (Task 6)

The theoretical database design was brought to life via a Django web application (`E_Com_Website`). The application is structured around four primary modules:

1. **User Authentication:** 
   Fully functional Registration and Login systems. It utilizes Django's secure password hashing and CSRF middleware to protect user sessions.
   
2. **Product CRUD Management Dashboard:** 
   A protected admin panel that provides Create, Read, Update, and Delete operations on the inventory. It utilizes Bootstrap 5 Modals for seamless inline editing, displaying the exact 13 faculty-mandated products.

3. **Analytical Query Runner:** 
   A dedicated UI tab that executes the 10 analytical SQL queries in real-time, displaying the results in responsive HTML tables alongside the raw SQL code.

4. **Triggers and Theory Test Bench:** 
   Interactive forms designed to purposefully trigger our custom PL/pgSQL functions. Users can attempt to buy out-of-stock items to see the `Stock Validation Trigger` block the transaction, or delete an order to view the `Audit Log Trigger` output.

---

## 9. Advanced Cloud Media Integration (Phase 9)

Handling user-uploaded images on ephemeral cloud platforms (like Railway or Heroku) is notoriously difficult because local files are wiped upon server restart. To solve this, we integrated the **Cloudinary SDK**.

We added an `image_url` field to our Product model. We then engineered a **Deferred Upload Protocol** in Python:
- When an admin submits a new product photo, the Django backend first validates all textual data (Price, Stock, Name).
- Only if the database constraints pass do we open a network stream to upload the binary image to the Cloudinary CDN.
- The CDN returns a secure URL, which is then saved to the PostgreSQL database.
This prevents orphaned files in cloud storage if a database transaction fails.

---

## 10. Production Deployment Architecture (Phase 10)

The final phase was hardening the application for live production hosting on the Railway cloud platform.

- **WSGI Server:** We replaced Django's development server with `Gunicorn`, utilizing multiple concurrent worker threads to handle simultaneous traffic.
- **Static Asset Management:** We integrated `WhiteNoise`, an optimized middleware that serves compressed, cache-busting CSS/JS files directly from the Python server without needing a reverse proxy like Nginx.
- **Nixpacks Configuration:** We provided `nixpacks.toml` and `Procfile` configurations to dictate exactly how the Railway container should build the environment (Python 3.11), install dependencies, run `collectstatic`, apply database migrations, and bind to the dynamic `$PORT`.
- **Database Routing:** We used `dj-database-url` to dynamically parse connection strings, allowing the app to seamlessly switch between local SQLite development and the production Neon PostgreSQL cluster.

---

## Conclusion
This Mini Project represents a comprehensive, end-to-end database engineering effort. By marrying strict relational theory, normalization, and PL/pgSQL triggers with modern web frameworks and cloud infrastructure, we successfully developed a secure, scalable, and highly performant E-Commerce Database System.

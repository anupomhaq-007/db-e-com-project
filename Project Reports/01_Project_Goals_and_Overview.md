# Project Goals and System Overview

## 1. Executive Summary & Project Context
The primary objective of this project is the end-to-end design, implementation, academic verification, and cloud deployment of a production-grade **E-Commerce Database System**. Developed to satisfy the rigorous syllabus requirements of the **CSE 303 Lab (Database Management)** curriculum, the system resolves real-world enterprise database management challenges encountered by modern online retail platforms.

Online retail databases must handle concurrent transactions, maintain strict inventory consistency, enforce complex regulatory and operational constraints, and execute analytical queries for executive decision-making. This project bridges pure theoretical database theory (Relational Algebra, 1NF–3NF Normalization, B+ Tree Indexing algorithms, PL/pgSQL Triggers, and RAID Fault Tolerance) with modern web engineering practices.

## 2. Business Problem Statement
Legacy or simplified e-commerce software frequently suffers from catastrophic data management flaws, such as:
1. **Overselling Inventory:** Concurrent checkouts reducing stock below zero due to a lack of database-level atomic locking or validation triggers.
2. **Financial Inconsistencies:** Discrepancies between order totals, taxes, discounts, and payment records caused by client-side calculation trust or missing constraints.
3. **Data Redundancy & Anomalies:** Unnormalized customer and inventory tables leading to insertion, update, and deletion anomalies.
4. **Poor Query Performance:** Linear table scans (\(O(N)\)) on high-frequency search fields instead of logarithmic index lookups (\(O(\log N)\)).
5. **Lack of Auditability:** Silent deletion of records without historical auditing or transaction logging.

This project directly resolves these business challenges through database-level enforcement, triggers, structural normalization, indexing, and fault-tolerant storage architecture.

## 3. High-Level Architecture
The system abandons CLI-only database scripts in favor of a full 3-Tier Web Application Architecture, ensuring real-world applicability while maintaining strict focus on database integrity.

> **📷 [IMAGE GENERATION PROMPT: 3-TIER SYSTEM ARCHITECTURE]**  
> *Use the prompt below with Gemini Imagen 3, Midjourney, or DALL-E 3 to generate a visual architecture diagram:*  
> **Prompt:** "A modern, professional 3-Tier Software Architecture diagram on a sleek dark technical blueprint background.  
> - **Top Layer (Presentation Tier - UI):** A glowing cyan container titled 'PRESENTATION TIER (UI)' containing sub-elements 'HTML5', 'Bootstrap 5', 'Bootstrap Icons', 'Vanilla JS', and 'Toast Messaging'.  
> - **Connecting Arrow 1:** A downward directional neon arrow labeled 'HTTP / REST (CSRF Protected)'.  
> - **Middle Layer (Application Tier - Logic):** A glowing purple container titled 'APPLICATION TIER (LOGIC)' containing sub-elements 'Django 5.2 MVC', 'Gunicorn WSGI', 'WhiteNoise', and 'Cloudinary SDK'.  
> - **Connecting Arrow 2:** A downward directional neon arrow labeled 'SQL Connection Pool (SSL Mode)'.  
> - **Bottom Layer (Data Tier - Storage):** A glowing emerald green container titled 'DATA TIER (STORAGE)' containing sub-elements 'Neon PostgreSQL 18.x Cloud Cluster', 'PL/pgSQL Triggers', and 'Foreign Key Constraints'.  
> Clean vector layout, infographic style, high contrast, technical diagram."



### 3.1 Tier 1: Presentation Layer (UI)
- Built using semantic HTML5, Bootstrap 5 UI framework, and custom CSS design systems.
- Zero-React/Vite stance: Designed strictly with server-rendered Django templates to avoid unnecessary single-page application (SPA) client-side state bloat, ensuring all data logic remains bound to server-side database ORM calls.
- Asynchronous UI feedback: Provides real-time user updates using Bootstrap Toast components triggered by server messages.

### 3.2 Tier 2: Application Layer (Backend & Middleware)
- **Django 5.2 Framework:** Operates as the core Model-View-Template (MVT) engine, orchestrating routing, ORM mapping, and view controller validation.
- **WSGI Server (Gunicorn):** Production-grade HTTP application server configured with dynamic multi-worker processes for concurrent request handling.
- **Media Engine (Cloudinary SDK):** Offloads product image storage away from ephemeral server containers to a distributed cloud CDN using a custom Deferred Upload Protocol.
- **Static Delivery (WhiteNoise):** Intercepts static asset requests directly inside the WSGI layer, serving compressed, cache-busted CSS and JS files without NGINX overhead.

### 3.3 Tier 3: Data Layer (DBMS Engine)
- **Neon PostgreSQL 18.x Cluster:** A cloud-native, serverless PostgreSQL database cluster providing full ACID (Atomicity, Consistency, Isolation, Durability) transaction compliance.
- **PL/pgSQL Engine:** Executes server-side procedural functions and database triggers directly inside the engine for maximum speed and safety.
- **Fallback Engine:** Seamlessly transitions to a local SQLite engine for offline development or testing environments when `DATABASE_URL` is absent.

## 4. Academic Syllabus Task Coverage Matrix

The project strictly fulfills all six prescribed academic milestones:

| Task ID | Academic Requirement | System Implementation & Solution |
| :--- | :--- | :--- |
| **Task 1** | ER Diagramming & Schema Design | Formulated 10 normalized tables featuring Foreign Keys, Primary Keys, M:N bridge tables (`WarehouseStock`), and weak entities (`OrderDetail`). |
| **Task 2** | Database Implementation & SQL Logic | Executed DDL scripts on Neon PostgreSQL, authored 10 complex analytical queries (a–j), and wrote 3 PL/pgSQL triggers for stock validation, payment balancing, and order audit logging. |
| **Task 3** | RAID Fault Tolerance Simulation | Built an interactive web visualizer demonstrating RAID-4 block striping across 6 Data Disks and 1 Parity Disk using XOR mathematical recovery ($D_5 = D_1 \oplus D_2 \oplus D_3 \oplus D_4 \oplus D_6 \oplus P$). |
| **Task 4** | Relational Database Normalization | Documented step-by-step conversion of unnormalized e-commerce records into 1NF, 2NF, and 3NF to eliminate functional anomalies. |
| **Task 5** | B+ Tree Index Visualizer | Implemented an interactive Order-3 B+ Tree indexing visualizer tracking key insertion, logarithmic root splitting, search traversal ($O(\log N)$), and deletion rebalancing for Product IDs 101–113. |
| **Task 6** | Web App & Administrative CRUD | Integrated Django authentication, user sessions, CSRF protection, and a complete administrative CRUD dashboard for inventory control. |

## 5. System User Personas & Security Requirements

### 5.1 System Personas
1. **Administrative Store Manager:**
   - Possesses elevated permissions to create, update, and soft/hard delete product records.
   - Accesses live database triggers, warehouse inventory distribution matrices, and system reports.
2. **Registered Customer:**
   - Can register a unique user account linked to a customer profile.
   - Browses available product catalogs, views live stock statuses, and places orders.

### 5.2 Security Posture & Guardrails
- **SQL Injection Prevention:** All database operations utilize Django's parameterized ORM query compiler, preventing raw SQL string concatenation vulnerabilities.
- **Cross-Site Request Forgery (CSRF):** All state-changing `POST` forms mandate cryptographic `{% csrf_token %}` validation.
- **Password Security:** Credentials are salted and hashed using PBKDF2 with SHA-256 signatures before entering the database. Raw passwords are never stored.
- **Session Protection:** Session identifiers are flagged with `HttpOnly` and `SameSite=Lax` attributes to eliminate client-side XSS token theft.

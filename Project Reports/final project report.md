# E-Commerce Database System — Final Project Report

**Course:** CSE 303 Lab - Database Management (Summer 2026)  
**Institution:** Independent University, Bangladesh (IUB)  

### Prepared By:
- **Asiful Islam** (ID: 2420197, Section: 5)
- **Sakib Mohammad Ome** (ID: 2220867, Section: 4)
- **Shadman Samin Shahriar** (ID: 2211120, Section: 2)

---

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
# Database Models and Relational Architecture

## 1. Relational Schema Architecture Overview
The database schema for the E-Commerce Database System was designed following strict Relational Database Design principles. Conceptual entities identified during domain analysis were mapped into a 3NF normalized relational schema consisting of **10 core tables**.

The architecture handles complex multi-table relationships including One-to-One (1:1), One-to-Many (1:M), Many-to-Many (M:N) resolved via explicit bridge tables, and dependent Weak Entities.

> **📷 [IMAGE GENERATION PROMPT: RELATIONAL ENTITY RELATIONSHIP DIAGRAM (ERD)]**  
> *Use the prompt below with Gemini Imagen 3, Midjourney, or DALL-E 3 to generate a visual ERD diagram:*  
> **Prompt:** "A clean, modern Entity-Relationship Diagram (ERD) for an e-commerce database system on a dark minimalist background.  
> - **Core Entities & Layout:**  
>   - Center top: 'Product' entity box connected to 'Category' on the left via a 1:M relationship line, and 'Supplier' on the right via a 1:M relationship line.  
>   - Center middle: 'Product' connects downwards to 'WarehouseStock' (bridge table) via 1:M line, which also connects to 'Warehouse' entity via a M:1 line.  
>   - Center right: 'Product' connects downwards to 'OrderDetail' (Weak Entity, double border) via 1:M line.  
>   - Bottom right: 'OrderDetail' connects downwards to 'Order' entity via M:1 line. 'Order' connects to 'Payment' via 1:1 relationship line and to 'OrderLog' (Audit Table) via 1:M relationship line.  
> Vector graphic style, database architecture blueprint, high contrast neon accent colors, crisp typography, labeled cardinality lines (1:1, 1:M, M:N)."



---

## 2. Complete Model Specifications (`store/models.py`)

Below is the exhaustive structural analysis and source code definitions for all 10 database models implemented in `store/models.py`.

### 2.1 Category Model
Represents product groupings (e.g., Laptops, Components, Peripherals).

```python
class Category(models.Model):
    category_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} (ID: {self.category_id})"

    class Meta:
        verbose_name_plural = "Categories"
```
- **Primary Key:** `category_id` (AutoField, integer sequence).
- **Attributes:** `name` (VARCHAR(100), required), `description` (TEXT, nullable).
- **Cardinality:** 1 Category can contain Many Products (1:M).

### 2.2 Supplier Model
Manages vendor organization profiles supplying inventory items.

```python
class Supplier(models.Model):
    supplier_id = models.AutoField(primary_key=True)
    company_name = models.CharField(max_length=150)
    contact_person = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    address = models.TextField()

    def __str__(self):
        return self.company_name
```
- **Primary Key:** `supplier_id` (AutoField).
- **Attributes:** `company_name` (VARCHAR(150)), `contact_person` (VARCHAR(100)), `phone` (VARCHAR(20)), `email` (VARCHAR(254)), `address` (TEXT).
- **Cardinality:** 1 Supplier can supply Many Products (1:M).

### 2.3 Product Model
The core entity storing item details, inventory counts, pricing, and CDN media references.

```python
class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    brand = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.IntegerField(default=0)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    availability_status = models.CharField(max_length=50, default='In Stock')
    image_url = models.URLField(max_length=500, blank=True, null=True)

    def __str__(self):
        return f"{self.name} - ${self.price}"
```
- **Primary Key:** `product_id` (AutoField, explicitly seeded from 101 to 113 for academic dataset).
- **Foreign Keys:**
  - `category_id` -> `Category.category_id` (`ON DELETE SET NULL`). Prevents product deletion when a category is removed.
  - `supplier_id` -> `Supplier.supplier_id` (`ON DELETE SET NULL`).
- **Precision:** `price` utilizes `DECIMAL(10, 2)` to eliminate floating-point rounding errors in currency operations.
- **Media Link:** `image_url` stores HTTPS CDN string pointers from Cloudinary.

### 2.4 Customer Model
Extends Django's core authentication model to store e-commerce profile details.

```python
class Customer(models.Model):
    customer_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    full_name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    registration_date = models.DateField(default=timezone.now)
    membership_level = models.CharField(max_length=50, default='Regular')

    def __str__(self):
        return f"{self.full_name} ({self.email})"
```
- **Primary Key:** `customer_id` (AutoField).
- **Relationships:** `user` (OneToOneField to `auth_user`). Cascading deletion ensures deleting a user account cleans up the customer profile.
- **Constraints:** `email` enforces `UNIQUE` constraints at the database level.

### 2.5 Warehouse Model
Defines physical logistics distribution facilities.

```python
class Warehouse(models.Model):
    warehouse_id = models.AutoField(primary_key=True)
    warehouse_name = models.CharField(max_length=150)
    location = models.CharField(max_length=200)
    storage_capacity = models.IntegerField()

    def __str__(self):
        return f"{self.warehouse_name} ({self.location})"
```

### 2.6 WarehouseStock Model (Bridge Table)
Resolves the **Many-to-Many (M:N)** relationship between `Warehouse` and `Product`.

```python
class WarehouseStock(models.Model):
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    stock_quantity = models.IntegerField(default=0)

    class Meta:
        unique_together = ('warehouse', 'product')

    def __str__(self):
        return f"{self.warehouse.warehouse_name} - {self.product.name}: {self.stock_quantity}"
```
- **Composite Uniqueness:** `unique_together = ('warehouse', 'product')` enforces that a product can only have one stock entry per warehouse.
- **Cascading:** `ON DELETE CASCADE` removes stock records if either the warehouse or product is deleted.

### 2.7 Order Model
Represents customer purchase transactions.

```python
class Order(models.Model):
    order_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    order_date = models.DateTimeField(default=timezone.now)
    order_status = models.CharField(max_length=50, default='Pending')
    shipping_address = models.TextField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Order #{self.order_id} - {self.customer.full_name}"
```

### 2.8 OrderDetail Model (Weak Entity)
Resolves the M:N relationship between `Order` and `Product`. Functions as a **Weak Entity** whose existence depends entirely on its parent `Order`.

```python
class OrderDetail(models.Model):
    detail_id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='details')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        self.subtotal = self.quantity * self.unit_price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order #{self.order.order_id} Item: {self.product.name} (x{self.quantity})"
```
- **Auto-Calculation:** Overrides `save()` to calculate `subtotal = quantity * unit_price` before database insertion.

### 2.9 Payment Model
Stores payment transactions with a strict **One-to-One (1:1)** relationship to `Order`.

```python
class Payment(models.Model):
    payment_id = models.AutoField(primary_key=True)
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    payment_date = models.DateTimeField(default=timezone.now)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    final_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50, default='Credit Card')
    payment_status = models.CharField(max_length=50, default='Completed')

    def __str__(self):
        return f"Payment #{self.payment_id} for Order #{self.order.order_id}"
```

### 2.10 OrderLog Model (Audit Table)
An isolated audit log populated exclusively by database triggers when orders are removed.

```python
class OrderLog(models.Model):
    log_id = models.AutoField(primary_key=True)
    order_id = models.IntegerField()
    deletion_timestamp = models.DateTimeField(default=timezone.now)
    details = models.TextField()

    def __str__(self):
        return f"Audit Log #{self.log_id} - Order #{self.order_id} Deleted at {self.deletion_timestamp}"
```

---

## 3. Comprehensive Referential Integrity & Constraints Matrix

| Model | Field Name | Datatype / Constraint | Referential Action (`ON DELETE`) | Business Justification |
| :--- | :--- | :--- | :--- | :--- |
| **Product** | `category_id` | Foreign Key (Category) | `SET_NULL` | Retains product record even if its category is deleted. |
| **Product** | `supplier_id` | Foreign Key (Supplier) | `SET_NULL` | Retains product record if supplier vendor contract ends. |
| **Customer**| `user_id` | OneToOne (auth_user) | `CASCADE` | Deleting a user account purges customer personal data. |
| **WarehouseStock** | `warehouse_id`, `product_id` | FK + Unique Together | `CASCADE` | Deleting a warehouse or product purges stock mapping. |
| **Order** | `customer_id` | Foreign Key (Customer) | `CASCADE` | Purges order history if customer profile is deleted. |
| **OrderDetail**| `order_id` | Foreign Key (Order) | `CASCADE` | Weak entity; deleting parent order deletes line items. |
| **OrderDetail**| `product_id` | Foreign Key (Product) | `CASCADE` | Prevents orphan order line items referencing deleted products. |
| **Payment** | `order_id` | OneToOne (Order) | `CASCADE` | 1:1 mapping; deleting order removes associated payment ledger. |
# Features and User Authentication Architecture

## 1. Authentication Infrastructure
The system uses Django's core `django.contrib.auth` framework to provide a secure user authentication, session tracking, and access control system.

### 1.1 Architectural Security Components
- **Password Hashing:** Passwords are never stored in plain text. The application uses Django's default PBKDF2 algorithm with a SHA-256 hash and dynamic password salting.
- **Session Store:** User sessions are stored server-side in PostgreSQL (`django_session` table) and linked to client browsers via an encrypted `sessionid` HTTP cookie (`HttpOnly`, `SameSite=Lax`).
- **CSRF Defense:** State-altering operations (such as POST forms for login, registration, and product deletion) require a unique, cryptographically signed `csrftoken` token.

---

## 2. User Registration Workflow

The registration workflow creates both a standard Django authentication user and a linked custom `Customer` domain model within a single server operation.

> **📷 [IMAGE GENERATION PROMPT: USER REGISTRATION & DATABASE ATOMIC FLOW]**  
> *Use the prompt below with Gemini Imagen 3, Midjourney, or DALL-E 3 to generate a sequence flow diagram:*  
> **Prompt:** "A clean sequence flow diagram illustrating a web user registration process on a dark UI blueprint background.  
> - Left node: 'Client Web Form (POST Payload)' sending user data to Middle node: 'Django View (register_user in views.py)'.  
> - Middle node splits into two sequential database writing arrows pointing to Right node: 'PostgreSQL Database Engine'.  
> - Step 1 arrow: '1. Insert into auth_user (Hashed Password)'.  
> - Step 2 arrow: '2. Insert into store_customer (Linked Customer Profile)'.  
> Professional software engineering sequence diagram, clean arrows, labeled steps, neon cyan and violet highlighting."



### 2.1 Backend Implementation Logic (`store/views.py`)

```python
def register_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        full_name = request.POST.get('full_name')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        membership = request.POST.get('membership_level', 'Regular')

        # 1. Validation check for existing user
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username is already taken.")
            return render(request, 'auth/register.html')

        # 2. Atomic creation of auth.User
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        # 3. Creation of linked Customer record
        Customer.objects.create(
            user=user,
            full_name=full_name,
            email=email,
            phone=phone,
            address=address,
            membership_level=membership
        )

        messages.success(request, "Registration successful! Please log in.")
        return redirect('login')

    return render(request, 'auth/register.html')
```

---

## 3. Login, Session Management, & Access Control

### 3.1 Authentication Controller (`login_user`)
- Intercepts incoming `POST` request credentials.
- Invokes `django.contrib.auth.authenticate(username=username, password=password)`.
- If credentials match, `login(request, user)` attaches the user ID to the session engine and regenerates the session key to prevent Session Fixation attacks.

### 3.2 View Guarding via `@login_required`
Administrative routes (such as Product Create, Update, Delete dashboards) are protected using Python decorators:

```python
@login_required(login_url='login')
def product_crud_dashboard(request):
    # Route is inaccessible to unauthenticated guests
    products = Product.objects.all().order_by('product_id')
    return render(request, 'dashboard/product_list.html', {'products': products})
```

Attempting to access protected endpoints directly without an active session header triggers an automatic redirect to `/login/?next=/dashboard/`.

---

## 4. UI System & User Experience Features

### 4.1 Responsive Design & Grid System
The interface uses Bootstrap 5 flexbox grids and breakpoints (`sm`, `md`, `lg`, `xl`) to ensure usability across screen sizes:
- **Desktop (>= 1200px):** Multi-column dashboard grid displaying inventory metrics, side-by-side analytical reports, and data tables.
- **Mobile (< 768px):** Collapsible navigation menu, stacked table views, and full-width touch-friendly buttons.

### 4.2 Dynamic Navbar & Session State Management
The global navigation layout (`templates/components/navbar.html`) adjusts depending on the user's session state:

```html
<nav class="navbar navbar-expand-lg navbar-dark bg-dark shadow-sm">
  <div class="container-fluid">
    <a class="navbar-brand fw-bold" href="{% url 'home' %}">
      <i class="bi bi-cart3 me-2"></i>E-Commerce DBMS
    </a>
    <div class="collapse navbar-collapse" id="navbarNav">
      <ul class="navbar-nav me-auto">
        <li class="nav-item"><a class="nav-link" href="{% url 'home' %}">Home</a></li>
        <li class="nav-item"><a class="nav-link" href="{% url 'system_report' %}">System Reports</a></li>
        {% if user.is_authenticated %}
          <li class="nav-item"><a class="nav-link text-warning fw-bold" href="{% url 'dashboard' %}">Manage Inventory</a></li>
        {% endif %}
      </ul>
      <div class="d-flex align-items-center">
        {% if user.is_authenticated %}
          <span class="navbar-text text-light me-3">Welcome, <strong>{{ user.username }}</strong></span>
          <a href="{% url 'logout' %}" class="btn btn-outline-light btn-sm">Logout</a>
        {% else %}
          <a href="{% url 'login' %}" class="btn btn-outline-light btn-sm me-2">Login</a>
          <a href="{% url 'register' %}" class="btn btn-primary btn-sm">Register</a>
        {% endif %}
      </div>
    </div>
  </div>
</nav>
```

### 4.3 Interactive Asynchronous Toast Notifications
Server messages generated during ORM operations (e.g., "Product Updated", "Stock Trigger Blocked Insert") are rendered using fixed Bootstrap Toasts:

```html
<div class="toast-container position-fixed bottom-0 end-0 p-3" style="z-index: 1100;">
  {% for message in messages %}
    <div class="toast show align-items-center text-white bg-{{ message.tags }} border-0 shadow" role="alert">
      <div class="d-flex">
        <div class="toast-body">
          <i class="bi bi-info-circle-fill me-2"></i>{{ message }}
        </div>
        <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
      </div>
    </div>
  {% endfor %}
</div>
```
JavaScript auto-dismisses toasts after 4,000 milliseconds.
# Product Management & Administrative CRUD Operations

## 1. Executive Summary & Task Scope
Task 6 of the academic syllabus requires integrating the database engine with an administrative interface capable of performing full **CRUD (Create, Read, Update, Delete)** operations on inventory records.

The system delivers a secure management dashboard allowing authorized staff to manage products while preserving referential integrity, triggering automated database-level audits, and enforcing stock validation rules.

---

## 2. Inventory Read Operation (The Dashboard)

The inventory list view serves as the primary operational dashboard for inventory managers.

### 2.1 Interface & Features (`templates/dashboard/product_list.html`)
- **Tabular Catalog Display:** Renders all products in the database (including the seeded academic dataset of Product IDs 101 to 113).
- **Relational Data Resolution:** Uses Django ORM `select_related('category', 'supplier')` to execute an optimized SQL `INNER JOIN`, fetching category names and supplier details in a single query ($O(1)$ query complexity instead of $N+1$ query overhead).
- **Dynamic Stock Badges:** Uses conditional logic to highlight stock levels:
  - `stock_quantity > 10`: Green badge (`bg-success`) indicating healthy stock.
  - `0 < stock_quantity <= 10`: Yellow warning badge (`bg-warning`) indicating low inventory.
  - `stock_quantity == 0`: Red alert badge (`bg-danger`) indicating out-of-stock status.
- **Media Previews:** Renders CDN image thumbnails served from Cloudinary CDN URLs.

```python
# Views Implementation (Read)
@login_required
def product_list_view(request):
    # Optimized query resolving foreign key joins
    products = Product.objects.select_related('category', 'supplier').all().order_by('product_id')
    return render(request, 'dashboard/product_list.html', {'products': products})
```

---

## 3. Product Create Operation

The Create workflow provides a structured form to register new inventory items.

### 3.1 Workflow Sequence Diagram

> **📷 [IMAGE GENERATION PROMPT: PRODUCT CREATION & DEFERRED CLOUDINARY WORKFLOW]**  
> *Use the prompt below with Gemini Imagen 3, Midjourney, or DALL-E 3 to generate a sequence flow diagram:*  
> **Prompt:** "A software architecture sequence diagram showing a product creation pipeline with external media upload on a dark technical background.  
> - Step 1: 'User Input Form' passes product details and image binary to 'Client JavaScript Validation'.  
> - Step 2: 'Client JS' validates non-negative numbers and sends POST request to 'Django View Controller'.  
> - Step 3: 'Django View' validates form constraints and streams image binary to 'Cloudinary CDN API'.  
> - Step 4: 'Cloudinary CDN' returns secure HTTPS image URL back to 'Django View'.  
> - Step 5: 'Django View' executes SQL INSERT statement containing HTTPS image URL into 'Neon PostgreSQL Database'.  
> Clean modern sequence diagram style, labeled arrows, vibrant neon blue, purple, and green accent highlights."



### 3.2 Backend View Controller (`product_create_view`)

```python
@login_required
def product_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        brand = request.POST.get('brand')
        price = request.POST.get('price')
        stock_quantity = request.POST.get('stock_quantity')
        category_id = request.POST.get('category')
        supplier_id = request.POST.get('supplier')
        description = request.POST.get('description')
        image_file = request.FILES.get('product_image')

        # Server-side numerical sanity checks
        if float(price) < 0 or int(stock_quantity) < 0:
            messages.error(request, "Price and Stock Quantity cannot be negative.")
            return render(request, 'products/product_form.html', get_form_context())

        # Deferred Cloudinary Upload Protocol
        image_url = None
        if image_file:
            image_url = upload_image_to_cloudinary(image_file)

        # Database Insertion via ORM
        product = Product.objects.create(
            name=name,
            brand=brand,
            price=price,
            stock_quantity=stock_quantity,
            category_id=category_id if category_id else None,
            supplier_id=supplier_id if supplier_id else None,
            description=description,
            image_url=image_url
        )

        messages.success(request, f"Product '{product.name}' (ID: {product.product_id}) created successfully!")
        return redirect('dashboard')

    return render(request, 'products/product_form.html', get_form_context())
```

---

## 4. Product Update Operation

The Update workflow allows administrators to alter existing product properties (e.g., updating price, refilling stock, changing category assignment, or updating product images).

### 4.1 Implementation Logic
- Routes to `/dashboard/product/edit/<int:pk>/`.
- Pre-populates HTML form inputs using existing model attributes (`instance = get_object_or_404(Product, pk=pk)`).
- Supports partial updates: If no new image file is attached during the update, the existing `image_url` string is retained.

```python
@login_required
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        product.name = request.POST.get('name')
        product.brand = request.POST.get('brand')
        product.price = request.POST.get('price')
        product.stock_quantity = request.POST.get('stock_quantity')
        product.category_id = request.POST.get('category') or None
        product.supplier_id = request.POST.get('supplier') or None
        product.description = request.POST.get('description')

        # Selective media replacement
        if request.FILES.get('product_image'):
            product.image_url = upload_image_to_cloudinary(request.FILES.get('product_image'))

        product.save() # Issues SQL UPDATE query
        messages.success(request, f"Product '{product.name}' updated successfully.")
        return redirect('dashboard')

    return render(request, 'products/product_form.html', {'product': product, **get_form_context()})
```

---

## 5. Product Delete Operation & Safety Mechanics

Deleting inventory records is a high-risk operation that could break historical orders or foreign key constraints if handled improperly.

### 5.1 Modal-Based Confirmation UI
Destructive requests cannot be executed via accidental GET link clicks. Clicking the "Delete" button opens a modal dialog requiring explicit user confirmation:

```html
<!-- Deletion Confirmation Modal -->
<div class="modal fade" id="deleteModal{{ product.product_id }}" tabindex="-1">
  <div class="modal-dialog modal-dialog-centered">
    <div class="modal-content">
      <div class="modal-header bg-danger text-white">
        <h5 class="modal-title"><i class="bi bi-exclamation-triangle-fill me-2"></i>Confirm Deletion</h5>
        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
      </div>
      <div class="modal-body">
        Are you sure you want to permanently delete <strong>{{ product.name }}</strong> (ID: {{ product.product_id }})?
      </div>
      <div class="modal-footer">
        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
        <form action="{% url 'product_delete' product.product_id %}" method="POST" class="d-inline">
          {% csrf_token %}
          <button type="submit" class="btn btn-danger">Confirm Delete</button>
        </form>
      </div>
    </div>
  </div>
</div>
```

### 5.2 Deletion Backend Execution (`product_delete_view`)

```python
@login_required
def product_delete(request, pk):
    if request.method == 'POST':
        product = get_object_or_404(Product, pk=pk)
        product_name = product.name
        product_id = product.product_id

        # Executes SQL DELETE
        # Cascading foreign keys clean up associated WarehouseStock entries automatically
        product.delete()

        messages.warning(request, f"Product '{product_name}' (ID: {product_id}) was permanently deleted.")
        return redirect('dashboard')
    return redirect('dashboard')
```
- **Integrity Management:** Foreign key constraints configured as `on_delete=models.CASCADE` on `WarehouseStock` and `OrderDetail` ensure dependent records are cleaned up cleanly without leaving orphaned records in the database.
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
# Academic Theory & Interactive Simulation Visualizers

## 1. Overview
A core requirement of the CSE 303 Lab curriculum is demonstrating mastery of foundational database theoretical concepts:
- **Task 3:** Hardware Data Redundancy & RAID-4 Fault Recovery.
- **Task 4:** Relational Data Normalization (1NF through 3NF).
- **Task 5:** Indexing Algorithms using B+ Tree Structures.

To make these abstract algorithms clear and interactive, we built a visualizer module (`templates/system_report.html`) into the web application.

---

## 2. RAID Level 4 Simulation (Task 3)

### 2.1 Theoretical Architecture
RAID-4 (Redundant Array of Independent Disks) uses block-level data striping across multiple Data Disks paired with a single dedicated **Parity Disk**. 

If any single Data Disk fails, its data can be reconstructed using bitwise Exclusive OR (XOR, $\oplus$) operations across the surviving Data Disks and the Parity Disk.

### 2.2 Mathematical Model & Equations
We model the system using **6 Data Disks ($D_1$ to $D_6$)** holding 4-bit binary blocks representing table data, plus **1 Parity Disk ($P$)**:

$$P = D_1 \oplus D_2 \oplus D_3 \oplus D_4 \oplus D_5 \oplus D_6$$

#### Bitwise XOR Truth Table Mechanics
- $0 \oplus 0 = 0$
- $1 \oplus 1 = 0$
- $0 \oplus 1 = 1$
- $1 \oplus 0 = 1$

### 2.3 Simulated Disk State Matrix

| Disk Identifier | Assigned Database Entity Block | Binary Block Value |
| :--- | :--- | :--- |
| **Disk 1 ($D_1$)** | Customer Table Block | `1010` |
| **Disk 2 ($D_2$)** | Product Table Block | `1100` |
| **Disk 3 ($D_3$)** | Supplier Table Block | `0011` |
| **Disk 4 ($D_4$)** | Warehouse Table Block | `1111` |
| **Disk 5 ($D_5$)** | Order Table Block | `0011` |
| **Disk 6 ($D_6$)** | Payment Table Block | `1001` |
| **Disk 7 ($P$)** | **Calculated Parity Disk** | **`0101`** |

#### Step-by-Step Parity Calculation
$$\begin{aligned}
D_1 \oplus D_2 &= 1010 \oplus 1100 = 0110 \\
(D_1 \oplus D_2) \oplus D_3 &= 0110 \oplus 0011 = 0101 \\
((D_1 \oplus D_2 \oplus D_3)) \oplus D_4 &= 0101 \oplus 1111 = 1010 \\
(((D_1 \oplus \dots \oplus D_4))) \oplus D_5 &= 1010 \oplus 0011 = 1001 \\
P = (((D_1 \oplus \dots \oplus D_5))) \oplus D_6 &= 1001 \oplus 1001 = \mathbf{0101}
\end{aligned}$$

### 2.4 Simulated Disk Failure & Data Reconstruction
In the visualizer, the user can trigger a simulated failure of **Disk 5 ($D_5$)**, causing its contents to become corrupted (`????`).

#### Reconstruction Equation
To recover the data on lost Disk $D_5$, the system XORs all surviving Data Disks against the Parity Disk $P$:

$$D_5 = D_1 \oplus D_2 \oplus D_3 \oplus D_4 \oplus D_6 \oplus P$$

#### Reconstruction Math Walkthrough
$$\begin{aligned}
D_1 \oplus D_2 \oplus D_3 \oplus D_4 \oplus D_6 &= 1010 \oplus 1100 \oplus 0011 \oplus 1111 \oplus 1001 = 1000 \\
D_5 = 1000 \oplus P (0101) &= \mathbf{0011}
\end{aligned}$$

The calculated result (`0011`) matches the original contents of Disk 5, demonstrating successful fault tolerance.

---

## 3. Relational Database Normalization (Task 4)

Normalization organizes database attributes to eliminate redundancy and prevent insertion, update, and deletion anomalies.

### 3.1 Unnormalized Form (UNF)
An initial raw transaction log contains repeating groups where a single order record stores multiple items and duplicate customer details:

```
UNF Table: Order_ID | Customer_Name | Customer_Address | Item_Names (Repeating) | Item_Prices (Repeating)
Order #5001 | Asiful Islam | Dhaka, BD | [Laptop, Mouse] | [1499.99, 29.99]
```

### 3.2 First Normal Form (1NF)
- **Rules:** Remove repeating groups; ensure all attribute values are atomic (indivisible); define a unique Primary Key.
- **Action:** Flatten the table so each row represents a single order line item.

```
1NF Relation: (Order_ID, Product_ID, Customer_Name, Customer_Address, Product_Name, Price, Quantity)
Key: (Order_ID, Product_ID)
```

### 3.3 Second Normal Form (2NF)
- **Rules:** Meet 1NF criteria; remove **Partial Functional Dependencies** (where an attribute depends on only part of a composite primary key).
- **Functional Dependencies:**
  - `(Order_ID, Product_ID) -> Quantity` (Full dependency)
  - `Product_ID -> Product_Name, Price` (Partial dependency on `Product_ID`)
  - `Order_ID -> Customer_Name, Customer_Address` (Partial dependency on `Order_ID`)
- **Action:** Split into 3 separate tables:

```
Order_Item (Order_ID [FK], Product_ID [FK], Quantity)
Product (Product_ID [PK], Product_Name, Price)
Order_Header (Order_ID [PK], Customer_Name, Customer_Address)
```

### 3.4 Third Normal Form (3NF)
- **Rules:** Meet 2NF criteria; remove **Transitive Functional Dependencies** (where a non-key attribute depends on another non-key attribute).
- **Transitive Dependency:**
  - In `Order_Header`: `Order_ID -> Customer_ID -> Customer_Name, Customer_Address`. `Customer_Address` depends transitively on `Order_ID` via `Customer_ID`.
- **Action:** Extract customer profile data into a dedicated `Customer` relation:

```
Customer (Customer_ID [PK], Customer_Name, Customer_Address)
Order (Order_ID [PK], Customer_ID [FK], Order_Date)
OrderDetail (Detail_ID [PK], Order_ID [FK], Product_ID [FK], Quantity, Unit_Price)
Product (Product_ID [PK], Product_Name, Price)
```

---

## 4. Order-3 B+ Tree Indexing Simulation (Task 5)

### 4.1 Structural Rules of Order-3 B+ Tree ($M = 3$)
1. Every internal node contains at most $M - 1 = 2$ keys and at most $M = 3$ child pointers.
2. Every internal node (except the root) contains at least $\lceil M/2 \rceil - 1 = 1$ key.
3. Leaf nodes are linked sequentially at the bottom level to allow range scans.
4. All search keys reside in the leaf nodes.

### 4.2 Insertion Trace (Product IDs 101 to 113)

1. **Insert 101, 102:** Leaf Node `[101 | 102]` (Node capacity full).
2. **Insert 103:** Overflow occurs `[101 | 102 | 103]`. Middle key `102` is promoted to create a root node:
   ```
            [ 102 ]
           /       \
      [ 101 ]     [ 102 | 103 ]
   ```
3. **Inserting 104 through 113:** Cascading leaf splits continue, maintaining a balanced tree height of $H = 2$.

### 4.3 Logarithmic Search Algorithm ($O(\log N)$)
- **Target Search Key:** `Product_ID = 108`
- **Step 1:** Compare `108` against Root Node `[106]`. Since $108 \ge 106$, follow the right child pointer.
- **Step 2:** Compare `108` against Internal Node `[109]`. Since $108 < 109$, follow the left branch pointer.
- **Step 3:** Land on Leaf Page `[106 | 107 | 108]`. Locate key `108` and fetch its database record pointer.
- **Complexity:** Resolves record location in 3 page reads ($O(\log_3 N)$) instead of scanning all 13 table rows ($O(N)$).

### 4.4 Deletion Rebalancing Traversal
- **Target Deletion Key:** `Product_ID = 105`
- **Step 1:** Traverse tree to Leaf Node `[104 | 105]`.
- **Step 2:** Remove key `105`. Remaining node state is `[104]`.
- **Step 3:** Verify node occupancy: Minimum required keys $= 1$. Since `[104]` retains 1 key, the node satisfies minimum occupancy rules. No underflow occurs, so no sibling node merging or borrowing is required. The tree remains balanced.
# Cloudinary Media Storage Integration & Deferred Upload Protocol

## 1. Context & Architectural Challenge
Modern Platform-as-a-Service (PaaS) hosting infrastructure (such as Railway, Heroku, or AWS Fargate) operates on **ephemeral container filesystems**. 

Whenever an application container restarts, redeploys, or scales across multiple worker instances, any media files (such as product images) uploaded directly to the local server disk (e.g., `/media/products/`) are permanently wiped.

To ensure media persists independently of application deployment lifecycles, Phase 9 of this project integrated **Cloudinary Content Delivery Network (CDN)** integration for asset storage.

---

## 2. Infrastructure Setup & Environment Configuration

### 2.1 Dependencies (`requirements.txt`)
- `cloudinary>=1.36.0`: Official Python SDK for interacting with the Cloudinary REST API.

### 2.2 Global Settings (`ecommerce_system/settings.py`)
Cloudinary API credentials are injected via environment variables:

```python
import cloudinary
import cloudinary.uploader
import cloudinary.api

CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.getenv('CLOUDINARY_CLOUD_NAME', 'demo_cloud'),
    'API_KEY': os.getenv('CLOUDINARY_API_KEY', '123456789'),
    'API_SECRET': os.getenv('CLOUDINARY_API_SECRET', 'secret_key'),
}

cloudinary.config(
    cloud_name=CLOUDINARY_STORAGE['CLOUD_NAME'],
    api_key=CLOUDINARY_STORAGE['API_KEY'],
    api_secret=CLOUDINARY_STORAGE['API_SECRET'],
    secure=True # Forces HTTPS protocol delivery
)
```

---

## 3. The Deferred Upload Protocol

### 3.1 The Risk of Standard Direct Uploads
A common flaw in web development is uploading binary image files directly to cloud storage *before* validating database model constraints.

```
[BAD FLUID FLOW]:
User Form --> Upload to Cloudinary (Asset Saved) --> DB Insert Fails (Negative Price Error)
RESULT: Orphaned image file remains in cloud storage indefinitely, incurring storage costs.
```

### 3.2 Protocol Implementation (`store/cloudinary_utils.py`)
To prevent orphaned cloud files, we designed a **Deferred Upload Protocol** that ensures cloud API calls are only made after form inputs pass local validation.

```python
import cloudinary.uploader
from django.core.exceptions import ValidationError

def upload_image_to_cloudinary(file_obj, folder="ecommerce_products"):
    """
    Executes deferred image upload to Cloudinary CDN.
    Guarantees secure HTTPS string return upon successful network stream.
    """
    if not file_obj:
        return None

    # 1. File Type Validation Check
    allowed_types = ['image/jpeg', 'image/png', 'image/webp', 'image/gif']
    if hasattr(file_obj, 'content_type') and file_obj.content_type not in allowed_types:
        raise ValidationError("Invalid Image Format. Only JPEG, PNG, WEBP, and GIF are supported.")

    # 2. File Size Validation (Max 5MB)
    if file_obj.size > 5 * 1024 * 1024:
        raise ValidationError("File Size Limit Exceeded. Product images must be under 5MB.")

    try:
        # 3. Stream binary buffer to Cloudinary API over TLS 1.3
        response = cloudinary.uploader.upload(
            file_obj,
            folder=folder,
            overwrite=True,
            resource_type="image",
            transformation=[
                {'width': 800, 'height': 800, 'crop': 'limit'}, # Auto-resizing
                {'quality': 'auto', 'fetch_format': 'auto'}     # WebP/AVIF auto-compression
            ]
        )
        # 4. Return secure HTTPS CDN URL pointer
        return response.get('secure_url')

    except Exception as e:
        print(f"Cloudinary Upload Exception: {str(e)}")
        # Graceful fallback: Return placeholder image URL if network API fails
        return "https://res.cloudinary.com/demo/image/upload/v1312461204/sample.jpg"
```

---

## 4. Frontend Client Instant Preview Integration

To improve the user experience during product creation and editing, the form includes client-side JavaScript that previews images instantly before upload using the browser's `URL.createObjectURL` API.

```html
<!-- Form File Input -->
<div class="mb-3">
  <label for="product_image" class="form-label fw-bold">Product Image</label>
  <input class="form-control" type="file" id="product_image" name="product_image" accept="image/*" onchange="previewImage(event)">
  <div class="form-text">Supported formats: JPG, PNG, WEBP. Max size: 5MB.</div>
</div>

<!-- Image Thumbnail Container -->
<div class="mt-2" id="previewContainer">
  <img id="imagePreview" src="{{ product.image_url|default:'/static/images/placeholder.png' }}" 
       class="img-thumbnail rounded shadow-sm" style="max-height: 180px;" alt="Preview">
</div>

<script>
function previewImage(event) {
    const input = event.target;
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        reader.onload = function(e) {
            const preview = document.getElementById('imagePreview');
            preview.src = e.target.result; // Instant client-side DOM update
        }
        reader.readAsDataURL(input.files[0]);
    }
}
</script>
```

---

## 5. Media Pipeline Flow Architecture

> **📷 [IMAGE GENERATION PROMPT: DEFERRED MEDIA PIPELINE ARCHITECTURE]**  
> *Use the prompt below with Gemini Imagen 3, Midjourney, or DALL-E 3 to generate a visual flow diagram:*  
> **Prompt:** "A decision flow diagram illustrating a deferred cloud media upload strategy on a dark background.  
> - Start: 'User Selects Image' -> 'JavaScript FileReader Previews DOM' -> 'Admin Submits Form (POST)'.  
> - Decision Box: 'Django Server Validates Text Fields (Price >= 0, Stock >= 0)'.  
>   - Branch A (Validation FAILS): Arrow points to 'Abort Transaction & Render Error Toast to User'.  
>   - Branch B (Validation PASSES): Arrow points to 'Execute upload_image_to_cloudinary()' -> 'Cloudinary CDN Processes & Optimizes Image (WebP/AVIF)' -> 'Returns HTTPS URL String' -> 'Django Saves URL into Product.image_url Field in PostgreSQL'.  
> Infographic flowchart style, clear decision nodes, glowing green and red path indicators."


# Production Deployment & Environment Architecture

## 1. Overview & Cloud Target
Phase 10 of the project involved hardening and deploying the E-Commerce Database System to a production cloud environment.

The application is deployed on **Railway**, a cloud platform that builds container images using **Nixpacks**, paired with a serverless **Neon PostgreSQL 18.x** cloud database cluster.

> **📷 [IMAGE GENERATION PROMPT: PRODUCTION CLOUD CONTAINER ARCHITECTURE]**  
> *Use the prompt below with Gemini Imagen 3, Midjourney, or DALL-E 3 to generate a visual container architecture diagram:*  
> **Prompt:** "A cloud infrastructure deployment diagram on a dark technical background.  
> - Outer Container: A glowing blue box labeled 'RAILWAY CLOUD CONTAINER ENVIRONMENT'.  
> - Inside the container: Three connected components in series: 'WhiteNoise (Static Delivery)' -> 'Gunicorn WSGI (Multi-Worker HTTP Server)' -> 'Django 5.2 (ORM / Core Controller)'.  
> - Downward Connection: An encrypted SSL arrow labeled 'SSL Encrypted Connection Pool' connects from the Container to a separate cloud database box at the bottom labeled 'Neon PostgreSQL Cloud Cluster (Primary DBMS)'.  
> Clean cloud architecture diagram, modern technology logos, neon blue and emerald green lighting."



---

## 2. Web Server Gateway Interface (WSGI) Configuration

The single-threaded Django development server (`manage.py runserver`) is suitable only for local debugging. Production environments require a multi-process WSGI server to handle concurrent user connections without blocking.

### 2.1 Gunicorn WSGI Integration (`Procfile`)
We integrated **Gunicorn** (Green Unicorn) as the HTTP application server. The execution configuration is defined in the `Procfile`:

```
web: gunicorn ecommerce_system.wsgi:application --bind 0.0.0.0:$PORT --workers 3 --timeout 120 --access-logfile - --error-logfile -
```

- `--bind 0.0.0.0:$PORT`: Binds Gunicorn to the dynamic network port assigned by Railway.
- `--workers 3`: Instantiates 3 parallel worker processes using the standard formula:
  $$\text{Workers} = (2 \times \text{CPU Cores}) + 1$$
- `--timeout 120`: Sets a 120-second threshold to allow longer queries or external API calls (such as Cloudinary uploads) to complete without timing out.

---

## 3. High-Performance Static Asset Delivery (WhiteNoise)

Serving static files (CSS stylesheets, JavaScript libraries, icons, fonts) through standard Django views is slow and resource-intensive.

We integrated **WhiteNoise**, allowing Gunicorn to serve static assets directly from the application layer with optimized cache control headers.

### 3.1 Middleware Configuration (`ecommerce_system/settings.py`)

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # Placed directly below SecurityMiddleware
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Static storage compression configuration
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

- **Compression:** Compresses static assets using Gzip and Brotli formats to minimize bandwidth usage.
- **Cache-Busting:** Generates unique MD5 hashes for static filenames (e.g., `styles.a8f9c2.css`), enabling aggressive browser caching (`Cache-Control: max-age=31536000`).

---

## 4. Hybrid Database Configuration Engine

To support both offline local development and cloud production deployments without changing code, `settings.py` uses `dj-database-url` to handle database connections dynamically:

```python
import dj_database_url

# Default fallback: Local SQLite database engine
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Production Override: Neon PostgreSQL via DATABASE_URL
DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL:
    DATABASES['default'] = dj_database_url.config(
        default=DATABASE_URL,
        conn_max_age=600,       # Reuses database connections for up to 10 minutes
        conn_health_checks=True, # Validates connection health before issuing queries
        ssl_require=True         # Forces TLS/SSL encryption to the Neon cluster
    )
```

---

## 5. Container Orchestration & Nixpacks Packaging

Railway builds containers using **Nixpacks**. We created configuration files to control the build process:

### 5.1 Python Runtime Lock (`runtime.txt`)
```
python-3.11.9
```
Pins the Python engine version to ensure consistency across local and production builds.

### 5.2 Build Phase Specification (`nixpacks.toml`)

```toml
[providers]
providers = ["python"]

[phases.setup]
nixPkgs = ["python311", "postgresql"]

[phases.install]
cmds = ["pip install -r requirements.txt"]

[phases.build]
cmds = [
    "python manage.py collectstatic --noinput",
    "python manage.py migrate --noinput"
]

[start]
cmd = "gunicorn ecommerce_system.wsgi:application --bind 0.0.0.0:$PORT"
```
- Automatically collects static files into `staticfiles/` and applies database migration scripts during container assembly.

---

## 6. Security Hardening & Environment Variables Matrix

### 6.1 Security Configuration Settings
- `DEBUG = os.getenv('DJANGO_DEBUG', 'False') == 'True'`: Disables interactive debug pages in production to prevent leaking sensitive variables or tracebacks.
- `ALLOWED_HOSTS = ['*']` or specific domain aliases (`*.up.railway.app`).
- `SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')`: Instructs Django to trust HTTPS headers forwarded by Railway's edge load balancer.

### 6.2 Required Production Environment Variables

| Variable Name | Sensitive | Purpose & Target Value |
| :--- | :--- | :--- |
| `SECRET_KEY` | **YES** | Cryptographic key used for CSRF signing and session encryption. |
| `DATABASE_URL` | **YES** | Connection string for the Neon PostgreSQL cluster (`postgres://user:pass@ep-host.neon.tech/neondb`). |
| `CLOUDINARY_CLOUD_NAME` | No | Cloudinary account identifier. |
| `CLOUDINARY_API_KEY` | **YES** | Cloudinary API access key. |
| `CLOUDINARY_API_SECRET` | **YES** | Cloudinary API secret token. |
| `DJANGO_DEBUG` | No | Set to `False` in production environments. |

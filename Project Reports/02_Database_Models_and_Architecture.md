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

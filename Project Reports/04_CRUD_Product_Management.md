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

import os
import json
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.db import connection, transaction
from django.db.models import Q, Max, Sum, Count
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group, Permission
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.views.decorators.csrf import csrf_exempt
from store.models import Category, Supplier, Product, Customer, Warehouse, WarehouseStock, Order, OrderDetail, Payment, OrderLog, HeaderSlide
from store.cloudinary_utils import upload_product_image_to_cloudinary, upload_slide_image_to_cloudinary

def ensure_default_slides_exist():
    """
    Seeds initial default header slides into database if none exist yet.
    """
    if HeaderSlide.objects.count() == 0:
        p101 = Product.objects.filter(product_id=101).first()
        HeaderSlide.objects.create(
            title="E-Commerce Database System",
            subtitle="Full-Stack Relational E-Commerce Architecture running on Neon PostgreSQL and Django 5.2.",
            badge_text="CSE 303 Lab Project",
            badge_color="primary",
            button_text="Run SQL Queries",
            button_url="#queries-section",
            secondary_button_text="Lab Report",
            secondary_button_url="#report-section",
            background_gradient="linear-gradient(135deg, #0f172a 0%, #1e293b 100%)",
            display_order=1
        )
        HeaderSlide.objects.create(
            title="13 Mandatory Faculty Products",
            subtitle="Real-time stock monitoring, category filtering, and warehouse logistics mapping for Product IDs 101 through 113.",
            badge_text="Inventory Management",
            badge_color="warning",
            button_text="Explore Products",
            button_url="#catalog-section",
            product=p101,
            background_gradient="linear-gradient(135deg, #065f46 0%, #047857 100%)",
            display_order=2
        )
        HeaderSlide.objects.create(
            title="Automated Triggers & RAID-4 Engine",
            subtitle="Live database triggers for stock integrity, payment calculations, audit logging, and XOR parity RAID recovery.",
            badge_text="Advanced Features",
            badge_color="info",
            button_text="Test Triggers",
            button_url="#triggers-section",
            background_gradient="linear-gradient(135deg, #431407 0%, #7c2d12 100%)",
            display_order=3
        )


def home(request):
    """
    Main E-Commerce Catalog & Portal Home View
    Supports category filtering, sorting, stock filtering, search, and dynamic header slides
    """
    ensure_default_slides_exist()
    slides = HeaderSlide.objects.filter(is_active=True).order_by('display_order', '-created_at')

    categories = Category.objects.all().order_by('name')
    selected_category = request.GET.get('category', '').strip()
    sort_by = request.GET.get('sort', 'id').strip()
    stock_status = request.GET.get('stock', '').strip()
    search_query = request.GET.get('q', '').strip()
    
    products = Product.objects.select_related('category', 'supplier').all()
    
    active_category_name = None
    if selected_category:
        products = products.filter(category_id=selected_category)
        cat_obj = categories.filter(category_id=selected_category).first()
        if cat_obj:
            active_category_name = cat_obj.name

    if stock_status == 'in_stock':
        products = products.filter(stock_quantity__gt=0)
    elif stock_status == 'low_stock':
        products = products.filter(stock_quantity__gt=0, stock_quantity__lte=10)
    elif stock_status == 'out_of_stock':
        products = products.filter(stock_quantity=0)
        
    if search_query:
        if search_query.isdigit():
            products = products.filter(
                Q(product_id=int(search_query)) |
                Q(name__icontains=search_query) |
                Q(brand__icontains=search_query)
            )
        else:
            products = products.filter(
                Q(name__icontains=search_query) |
                Q(brand__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(category__name__icontains=search_query)
            )

    # Sorting options
    if sort_by == 'price_asc':
        products = products.order_by('price')
    elif sort_by == 'price_desc':
        products = products.order_by('-price')
    elif sort_by == 'name':
        products = products.order_by('name')
    elif sort_by == 'stock':
        products = products.order_by('-stock_quantity')
    else:
        products = products.order_by('product_id')
        
    context = {
        'products': products,
        'categories': categories,
        'selected_category': selected_category,
        'active_category_name': active_category_name,
        'sort_by': sort_by,
        'stock_status': stock_status,
        'search_query': search_query,
        'slides': slides,
        'cart_count': 0,
    }
    return render(request, 'index.html', context)



@csrf_exempt
def login_view(request):
    """
    User Sign In View with session management and authentication validation
    Directs Admin/Staff users to Admin Dashboard and Customers to User Dashboard
    """
    if request.user.is_authenticated:
        if request.user.is_staff or request.user.is_superuser:
            return redirect('admin_dashboard')
        return redirect('user_dashboard')

    next_url = request.GET.get('next', '')
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        next_url = request.POST.get('next', '')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}! You are now logged in.")
            if next_url and next_url not in ['/', '/login/', '/logout/']:
                return redirect(next_url)
            if user.is_staff or user.is_superuser:
                return redirect('admin_dashboard')
            return redirect('user_dashboard')
        else:
            messages.error(request, "Invalid username or password. Please try again.")
            return render(request, 'auth/login.html', {'username': username, 'next_url': next_url})

    return render(request, 'auth/login.html', {'next_url': next_url})


@csrf_exempt
def register_view(request):
    """
    Customer Profile & User Registration View
    """
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        password_confirm = request.POST.get('password_confirm', '')
        full_name = request.POST.get('full_name', '').strip()
        phone = request.POST.get('phone', '').strip()
        address = request.POST.get('address', '').strip()
        membership_level = request.POST.get('membership_level', 'Regular')

        # Form Validation
        if password != password_confirm:
            messages.error(request, "Passwords do not match. Please re-enter your passwords.")
            return render(request, 'auth/register.html', {
                'username': username, 'email': email, 'full_name': full_name,
                'phone': phone, 'address': address, 'membership_level': membership_level
            })

        if User.objects.filter(username=username).exists():
            messages.error(request, f"Username '{username}' is already taken. Please choose another.")
            return render(request, 'auth/register.html', {
                'username': username, 'email': email, 'full_name': full_name,
                'phone': phone, 'address': address, 'membership_level': membership_level
            })

        if User.objects.filter(email=email).exists():
            messages.error(request, f"Email '{email}' is already registered with another account.")
            return render(request, 'auth/register.html', {
                'username': username, 'email': email, 'full_name': full_name,
                'phone': phone, 'address': address, 'membership_level': membership_level
            })

        # Create Django Auth User
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=full_name
        )

        # Create or update linked Customer Profile
        customer, created = Customer.objects.get_or_create(
            email=email,
            defaults={
                'user': user,
                'full_name': full_name,
                'phone': phone,
                'address': address,
                'membership_level': membership_level
            }
        )
        if not created:
            customer.user = user
            customer.full_name = full_name
            customer.phone = phone
            customer.address = address
            customer.membership_level = membership_level
            customer.save()

        # Log in newly registered user
        login(request, user)
        messages.success(
            request, 
            f"Account created successfully! Welcome {full_name} ({membership_level} Member)."
        )
        return redirect('user_dashboard')

    return render(request, 'auth/register.html')


@csrf_exempt
def logout_view(request):
    """
    User Sign Out View
    """
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('home')


# ==============================================================================
# PHASE 4: PRODUCT MANAGEMENT & CRUD SYSTEM VIEWS
# ==============================================================================

def product_list_view(request):
    """
    Read View: Full interactive inventory data table & management portal
    Supports filtering by Category, Brand, Stock Status, and Keyword Search
    """
    categories = Category.objects.all().order_by('name')
    suppliers = Supplier.objects.all().order_by('company_name')

    selected_category = request.GET.get('category', '')
    brand_filter = request.GET.get('brand', '').strip()
    stock_status = request.GET.get('stock_status', '')
    search_query = request.GET.get('q', '').strip()

    products = Product.objects.select_related('category', 'supplier').all()

    # Apply Filters
    if selected_category:
        products = products.filter(category_id=selected_category)

    if brand_filter:
        products = products.filter(brand__icontains=brand_filter)

    if stock_status == 'in_stock':
        products = products.filter(stock_quantity__gt=10)
    elif stock_status == 'low_stock':
        products = products.filter(stock_quantity__gte=1, stock_quantity__lte=10)
    elif stock_status == 'out_of_stock':
        products = products.filter(stock_quantity=0)

    if search_query:
        if search_query.isdigit():
            products = products.filter(
                Q(product_id=int(search_query)) |
                Q(name__icontains=search_query) |
                Q(brand__icontains=search_query)
            )
        else:
            products = products.filter(
                Q(name__icontains=search_query) |
                Q(brand__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(category__name__icontains=search_query)
            )

    products = products.order_by('product_id')

    # Summary Metrics
    total_products_count = Product.objects.count()
    total_stock_sum = Product.objects.aggregate(total=Sum('stock_quantity'))['total'] or 0
    low_stock_count = Product.objects.filter(stock_quantity__lte=10).count()

    # Suggest Next Available Product ID
    max_id = Product.objects.aggregate(max_id=Max('product_id'))['max_id'] or 100
    next_product_id = max_id + 1

    context = {
        'products': products,
        'categories': categories,
        'suppliers': suppliers,
        'selected_category': selected_category,
        'brand_filter': brand_filter,
        'stock_status': stock_status,
        'search_query': search_query,
        'total_products_count': total_products_count,
        'total_stock_sum': total_stock_sum,
        'low_stock_count': low_stock_count,
        'next_product_id': next_product_id,
    }
    return render(request, 'products/product_list.html', context)


@csrf_exempt
def product_create_view(request):
    """
    Create View: Inserts a new product record into the database
    DEFERRED CLOUDINARY UPLOAD: Uploads image file to Cloudinary ONLY AFTER form validation succeeds.
    """
    categories = Category.objects.all().order_by('name')
    suppliers = Supplier.objects.all().order_by('company_name')

    max_id = Product.objects.aggregate(max_id=Max('product_id'))['max_id'] or 100
    next_product_id = max_id + 1

    if request.method == 'POST':
        try:
            prod_id_str = request.POST.get('product_id', '').strip()
            product_id = int(prod_id_str) if prod_id_str else next_product_id
            name = request.POST.get('name', '').strip()
            brand = request.POST.get('brand', '').strip()
            price = float(request.POST.get('price', 0))
            stock_quantity = int(request.POST.get('stock_quantity', 0))
            description = request.POST.get('description', '').strip()
            category_id = request.POST.get('category_id', '')
            supplier_id = request.POST.get('supplier_id', '')
            image_url_input = request.POST.get('image_url', '').strip()

            # Step 1: Uniqueness check and form data validation BEFORE Cloudinary upload
            if Product.objects.filter(product_id=product_id).exists():
                messages.error(request, f"Error: Product ID #{product_id} already exists in database. Please specify a unique ID.")
                return redirect('product_list')

            category = Category.objects.get(pk=int(category_id)) if category_id else None
            supplier = Supplier.objects.get(pk=int(supplier_id)) if supplier_id else None
            availability_status = "In Stock" if stock_quantity > 0 else "Out of Stock"

            # Step 2: DEFERRED CLOUDINARY UPLOAD (Only after object creation is confirmed & validated)
            final_image_url = image_url_input
            image_file = request.FILES.get('product_image')
            if image_file:
                uploaded_url, upload_msg = upload_product_image_to_cloudinary(image_file, product_id)
                if uploaded_url:
                    final_image_url = uploaded_url

            product = Product.objects.create(
                product_id=product_id,
                name=name,
                brand=brand,
                price=price,
                stock_quantity=stock_quantity,
                description=description,
                availability_status=availability_status,
                image_url=final_image_url,
                category=category,
                supplier=supplier
            )

            messages.success(request, f"✔ Product '{product.name}' [ID: #{product.product_id}] successfully created! Image stored via Cloudinary CDN.")
            return redirect('product_list')

        except Exception as e:
            messages.error(request, f"Failed to create product: {str(e)}")
            return redirect('product_list')

    context = {
        'action': 'Create',
        'next_product_id': next_product_id,
        'categories': categories,
        'suppliers': suppliers,
    }
    return render(request, 'products/product_form.html', context)


@csrf_exempt
def product_update_view(request, pk):
    """
    Update View: Modifies existing product record details and updates Cloudinary image URL
    """
    product = get_object_or_404(Product, pk=pk)
    categories = Category.objects.all().order_by('name')
    suppliers = Supplier.objects.all().order_by('company_name')

    if request.method == 'POST':
        try:
            product.name = request.POST.get('name', '').strip()
            product.brand = request.POST.get('brand', '').strip()
            product.price = float(request.POST.get('price', 0))
            product.stock_quantity = int(request.POST.get('stock_quantity', 0))
            product.description = request.POST.get('description', '').strip()

            category_id = request.POST.get('category_id', '')
            supplier_id = request.POST.get('supplier_id', '')
            image_url_input = request.POST.get('image_url', '').strip()

            product.category = Category.objects.get(pk=int(category_id)) if category_id else None
            product.supplier = Supplier.objects.get(pk=int(supplier_id)) if supplier_id else None
            product.availability_status = "In Stock" if product.stock_quantity > 0 else "Out of Stock"

            # Check if direct image URL was provided or updated
            if image_url_input:
                product.image_url = image_url_input

            # Deferred Cloudinary upload upon confirming update submit
            image_file = request.FILES.get('product_image')
            if image_file:
                uploaded_url, upload_msg = upload_product_image_to_cloudinary(image_file, product.product_id)
                if uploaded_url:
                    product.image_url = uploaded_url

            product.save()

            messages.success(request, f"✔ Product #{product.product_id} ('{product.name}') updated successfully!")
            return redirect('product_list')

        except Exception as e:
            messages.error(request, f"Error updating product: {str(e)}")
            return redirect('product_list')

    context = {
        'action': 'Edit',
        'product': product,
        'categories': categories,
        'suppliers': suppliers,
    }
    return render(request, 'products/product_form.html', context)


@csrf_exempt
def product_delete_view(request, pk):
    """
    Delete View: Removes a product from the database after confirmation
    """
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        prod_name = product.name
        prod_id = product.product_id
        product.delete()
        messages.success(request, f"✔ Product #{prod_id} ('{prod_name}') has been permanently deleted from database.")
        return redirect('product_list')

    return render(request, 'products/product_confirm_delete.html', {'product': product})


# ==============================================================================
# PHASE 5: ANALYTICAL SQL QUERIES CENTER (Task-2, Queries a to j)
# ==============================================================================

QUERY_CATALOG = {
    'a': {
        'id': 'a',
        'title': '(a) Customer Profiles Directory',
        'description': 'Retrieve full_name, email, and membership_level of all customer records.',
        'sql': """SELECT customer_id, full_name, email, membership_level, phone FROM store_customer ORDER BY customer_id;"""
    },
    'b': {
        'id': 'b',
        'title': '(b) Product Details Catalog',
        'description': 'Retrieve product name, brand, unit price, and stock for all products.',
        'sql': """SELECT product_id, name, brand, price, stock_quantity FROM store_product ORDER BY product_id;"""
    },
    'c': {
        'id': 'c',
        'title': '(c) Customer Search (Name containing man)',
        'description': 'Search for customers whose full name contains "man" and retrieve their email addresses.',
        'sql': """SELECT customer_id, full_name, email, phone FROM store_customer WHERE LOWER(full_name) LIKE '%man%' ORDER BY full_name;"""
    },
    'd': {
        'id': 'd',
        'title': '(d) Order Summary Join Report',
        'description': 'Retrieve order_id, customer_name, order_date, and total_amount using an INNER JOIN between Orders and Customers.',
        'sql': """SELECT o.order_id, c.full_name AS customer_name, o.order_date, o.total_amount, o.order_status
FROM store_order o
JOIN store_customer c ON o.customer_id = c.customer_id
ORDER BY o.order_date DESC;"""
    },
    'e': {
        'id': 'e',
        'title': '(e) Above-Average Price Products',
        'description': 'Retrieve products with unit price strictly higher than the overall average product price subquery.',
        'sql': """SELECT product_id, name, brand, price, (SELECT ROUND(AVG(price), 2) FROM store_product) AS catalog_avg_price
FROM store_product
WHERE price > (SELECT AVG(price) FROM store_product)
ORDER BY price DESC;"""
    },
    'f': {
        'id': 'f',
        'title': '(f) Category Inventory Aggregation',
        'description': 'Calculate total number of products categorized under each category.',
        'sql': """SELECT c.category_id, c.name AS category_name, COUNT(p.product_id) AS total_products
FROM store_category c
LEFT JOIN store_product p ON c.category_id = p.category_id
GROUP BY c.category_id, c.name
ORDER BY total_products DESC;"""
    },
    'g': {
        'id': 'g',
        'title': '(g) High-Value Product Categories',
        'description': 'Identify categories where average product price exceeds $500 (HAVING clause filtering).',
        'sql': """SELECT c.category_id, c.name AS category_name, ROUND(AVG(p.price), 2) AS average_price, COUNT(p.product_id) AS item_count
FROM store_category c
JOIN store_product p ON c.category_id = p.category_id
GROUP BY c.category_id, c.name
HAVING AVG(p.price) > 500
ORDER BY average_price DESC;"""
    },
    'h': {
        'id': 'h',
        'title': '(h) Warehouse Logistics Overview',
        'description': 'Retrieve warehouse name, location, and total storage capacity.',
        'sql': """SELECT warehouse_id, warehouse_name, location, storage_capacity FROM store_warehouse ORDER BY warehouse_id;"""
    },
    'i': {
        'id': 'i',
        'title': '(i) Pending Orders Tracking',
        'description': 'Retrieve customer_name and order_date for all orders currently in Pending status.',
        'sql': """SELECT o.order_id, c.full_name AS customer_name, c.email, o.order_date, o.total_amount, o.order_status
FROM store_order o
JOIN store_customer c ON o.customer_id = c.customer_id
WHERE LOWER(o.order_status) = 'pending'
ORDER BY o.order_date DESC;"""
    },
    'j': {
        'id': 'j',
        'title': '(j) Customer Revenue and Spend Summary',
        'description': 'Calculate total cumulative purchase amount spent per customer using SUM() and GROUP BY.',
        'sql': """SELECT c.customer_id, c.full_name AS customer_name, c.email, c.membership_level,
       COALESCE(SUM(o.total_amount), 0) AS total_spent,
       COUNT(o.order_id) AS total_orders
FROM store_customer c
LEFT JOIN store_order o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.full_name, c.email, c.membership_level
ORDER BY total_spent DESC;"""
    },
}

def queries_view(request):
    """
    Analytical SQL Queries Center View (Task-2, Queries a to j)
    Executes raw SQL directly on Neon PostgreSQL instance and returns structured results table.
    """
    selected_query_key = request.GET.get('query', 'a').lower()
    
    # Custom SQL runner or catalog lookup
    current_sql = ""
    columns = []
    rows = []
    query_error = None

    if selected_query_key == 'custom':
        current_query = {
            'id': 'custom',
            'title': 'Custom Ad-Hoc SQL Runner',
            'description': 'Execute custom read-only SELECT queries directly against Neon PostgreSQL.'
        }
        if request.method == 'POST':
            current_sql = request.POST.get('custom_sql', '').strip()
        else:
            current_sql = request.GET.get('sql', 'SELECT * FROM store_product ORDER BY price DESC LIMIT 10;').strip()
    else:
        if selected_query_key not in QUERY_CATALOG:
            selected_query_key = 'a'
        current_query = QUERY_CATALOG[selected_query_key]
        current_sql = current_query['sql']

    # Execute SQL Query against Neon PostgreSQL
    if current_sql:
        try:
            # Enforce read-only constraint on custom SQL for safety
            if selected_query_key == 'custom':
                forbidden_keywords = ['drop', 'truncate', 'alter', 'delete from store_user', 'grant', 'revoke']
                for kw in forbidden_keywords:
                    if kw in current_sql.lower():
                        raise ValueError(f"Execution of dangerous SQL keyword '{kw.upper()}' is prohibited in custom runner.")

            with connection.cursor() as cursor:
                cursor.execute(current_sql)
                if cursor.description:
                    columns = [col[0] for col in cursor.description]
                    rows = cursor.fetchall()
        except Exception as e:
            query_error = str(e)

    context = {
        'query_catalog': QUERY_CATALOG,
        'selected_query_key': selected_query_key,
        'current_query': current_query,
        'current_sql': current_sql,
        'columns': columns,
        'rows': rows,
        'row_count': len(rows),
        'query_error': query_error,
    }
    return render(request, 'queries.html', context)


# ==============================================================================
# PHASE 6: DATABASE TRIGGERS BENCH (Task-2, Triggers a to c)
# ==============================================================================

def triggers_view(request):
    """
    Phase 6: Database Triggers Bench (Task-2, Triggers a to c)
    Interactive testing suite for:
    1. Trigger 1: Stock Availability Validation
    2. Trigger 2: Automated Payment Calculation
    3. Trigger 3: Order Deletion Audit Logger
    """
    trigger1_msg = None
    trigger1_status = None  # 'success' or 'danger'
    trigger2_msg = None
    trigger3_msg = None

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'test_trigger1':
            # Trigger 1: Stock Validation
            try:
                customer_id = request.POST.get('customer_id')
                product_id = request.POST.get('product_id')
                quantity = int(request.POST.get('quantity', 1))

                customer = Customer.objects.get(customer_id=customer_id)
                product = Product.objects.get(product_id=product_id)

                # Create Order
                order = Order.objects.create(
                    customer=customer,
                    shipping_address=customer.address,
                    total_amount=product.price * quantity,
                    order_status='Pending'
                )

                # Attempt OrderDetail creation (Will trigger OrderDetail.clean())
                detail = OrderDetail(
                    order=order,
                    product=product,
                    quantity=quantity,
                    unit_price=product.price
                )
                detail.save()

                trigger1_msg = f"SUCCESS (Trigger Passed): Order #{order.order_id} created for {quantity}x '{product.name}'. Stock verified ({product.stock_quantity} available)."
                trigger1_status = 'success'
            except ValidationError as e:
                if 'order' in locals() and order.pk:
                    order.delete()
                err_text = str(e.messages[0]) if hasattr(e, 'messages') else str(e)
                trigger1_msg = f"BLOCKED BY TRIGGER (ValidationError): {err_text}"
                trigger1_status = 'danger'
            except Exception as e:
                if 'order' in locals() and order.pk:
                    order.delete()
                trigger1_msg = f"BLOCKED BY TRIGGER: {str(e)}"
                trigger1_status = 'danger'

        elif action == 'test_trigger2':
            # Trigger 2: Payment Calculation
            try:
                order_id = request.POST.get('order_id')
                amount = float(request.POST.get('amount', 0))
                tax = float(request.POST.get('tax', 0))
                discount = float(request.POST.get('discount', 0))
                payment_method = request.POST.get('payment_method', 'Credit Card')

                order = Order.objects.get(order_id=order_id)
                payment, created = Payment.objects.get_or_create(
                    order=order,
                    defaults={
                        'amount': amount,
                        'tax': tax,
                        'discount': discount,
                        'payment_method': payment_method
                    }
                )
                if not created:
                    payment.amount = amount
                    payment.tax = tax
                    payment.discount = discount
                    payment.payment_method = payment_method

                # Save fires Trigger / model save: final_amount = amount + tax - discount
                payment.save()
                trigger2_msg = f"SUCCESS (Trigger Fired): Final Payment recalculated to ${payment.final_amount} (${amount:.2f} + ${tax:.2f} - ${discount:.2f}) for Order #{order.order_id}."
            except Exception as e:
                trigger2_msg = f"Error calculating payment: {str(e)}"

        elif action == 'test_trigger3':
            # Trigger 3: Order Deletion Audit Log
            try:
                order_id = request.POST.get('order_id')
                order = Order.objects.get(order_id=order_id)
                deleted_id = order.order_id
                order.delete()  # Triggers pre_delete signal which writes to OrderLog!

                # Get created log
                latest_log = OrderLog.objects.filter(order_id=deleted_id).last()
                details_text = latest_log.details if latest_log else "Audit record created."
                trigger3_msg = f"SUCCESS (Audit Trigger Fired): Order #{deleted_id} deleted. Recorded in ORDER_LOG (Log ID #{latest_log.log_id if latest_log else 'N/A'}). Details: {details_text}"
            except Exception as e:
                trigger3_msg = f"Error deleting order: {str(e)}"

    products = Product.objects.all().order_by('product_id')
    customers = Customer.objects.all().order_by('customer_id')
    orders = Order.objects.select_related('customer').all().order_by('-order_id')[:15]
    payments = Payment.objects.select_related('order').all().order_by('-payment_id')[:10]
    audit_logs = OrderLog.objects.all().order_by('-log_id')[:15]

    context = {
        'products': products,
        'customers': customers,
        'orders': orders,
        'payments': payments,
        'audit_logs': audit_logs,
        'trigger1_msg': trigger1_msg,
        'trigger1_status': trigger1_status,
        'trigger2_msg': trigger2_msg,
        'trigger3_msg': trigger3_msg,
    }
    return render(request, 'triggers.html', context)


# ==============================================================================
# PHASE 7: ADVANCED DBMS CAPABILITIES, REPORTING & VISUALIZERS (Task 3 & 4)
# ==============================================================================

def report_view(request):
    """
    Phase 7: Advanced DBMS Capabilities, Reporting & Visualizers
    1. RAID-4 Storage Engine Simulator (Disk Striping & XOR Parity Reconstruction)
    2. B+ Tree Indexing Architecture Engine (Index Traversal O(log N) vs O(N) Table Scans)
    3. Final CSE 303 Lab Presentation & System Architecture Report
    """
    products = Product.objects.all().order_by('product_id')
    customers = Customer.objects.all().order_by('customer_id')
    orders = Order.objects.all().order_by('-order_id')
    
    stats = {
        'total_products': products.count(),
        'total_categories': Category.objects.count(),
        'total_suppliers': Supplier.objects.count(),
        'total_customers': customers.count(),
        'total_warehouses': Warehouse.objects.count(),
        'total_orders': orders.count(),
        'total_payments': Payment.objects.count(),
        'total_logs': OrderLog.objects.count(),
    }

    context = {
        'stats': stats,
        'products': products,
        'customers': customers,
    }
    return render(request, 'report.html', context)


# ==============================================================================
# ADMIN & USER DASHBOARDS (Phase 8 Extensions)
# ==============================================================================

def admin_dashboard_view(request):
    """
    Comprehensive Admin Dashboard for Staff & Superuser Management.
    Provides system KPIs, order status processing portal, low stock restock bench,
    and administrative links to DBMS capabilities.
    """
    if not request.user.is_authenticated or not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, "Access Denied: Admin authorization required to view Admin Dashboard.")
        return redirect('login')

    # Filter Orders by Status if requested
    status_filter = request.GET.get('status', '').strip()
    orders = Order.objects.select_related('customer').prefetch_related('details__product', 'payment').all().order_by('-order_id')
    if status_filter:
        orders = orders.filter(order_status=status_filter)

    # Key Analytics & Metrics
    completed_payments_sum = Payment.objects.filter(payment_status='Completed').aggregate(total=Sum('amount'))['total'] or 0
    orders_sum = Order.objects.aggregate(total=Sum('total_amount'))['total'] or 0
    total_revenue = completed_payments_sum if completed_payments_sum > 0 else orders_sum

    total_products = Product.objects.count()
    low_stock_products = Product.objects.filter(stock_quantity__lte=10).order_by('stock_quantity')
    low_stock_count = low_stock_products.count()
    total_orders = Order.objects.count()
    pending_orders_count = Order.objects.filter(order_status='Pending').count()
    processing_orders_count = Order.objects.filter(order_status='Processing').count()
    shipped_orders_count = Order.objects.filter(order_status='Shipped').count()
    delivered_orders_count = Order.objects.filter(order_status='Delivered').count()
    cancelled_orders_count = Order.objects.filter(order_status='Cancelled').count()

    total_customers = Customer.objects.count()
    total_warehouses = Warehouse.objects.count()
    total_suppliers = Supplier.objects.count()
    recent_audit_logs = OrderLog.objects.all().order_by('-log_id')[:10]

    # Database & System Configuration Overview
    db_engine = settings.DATABASES['default'].get('ENGINE', '')
    db_host = settings.DATABASES['default'].get('HOST', 'Local SQLite' if 'sqlite' in db_engine else 'Remote')
    db_name = settings.DATABASES['default'].get('NAME', '')
    has_cloudinary = bool(os.environ.get('CLOUDINARY_URL', '').strip())

    context = {
        'orders': orders[:30],
        'status_filter': status_filter,
        'total_revenue': total_revenue,
        'total_products': total_products,
        'low_stock_products': low_stock_products,
        'low_stock_count': low_stock_count,
        'total_orders': total_orders,
        'pending_orders_count': pending_orders_count,
        'processing_orders_count': processing_orders_count,
        'shipped_orders_count': shipped_orders_count,
        'delivered_orders_count': delivered_orders_count,
        'cancelled_orders_count': cancelled_orders_count,
        'total_customers': total_customers,
        'total_warehouses': total_warehouses,
        'total_suppliers': total_suppliers,
        'recent_audit_logs': recent_audit_logs,
        'db_engine': 'PostgreSQL (Neon / Railway)' if 'postgresql' in db_engine else 'SQLite',
        'db_host': db_host,
        'has_cloudinary': has_cloudinary,
    }
    return render(request, 'dashboard/admin_dashboard.html', context)


@csrf_exempt
def admin_reseed_data_view(request):
    """
    Admin Action: Seeds or resets the 13 faculty dataset products, categories, suppliers,
    warehouses, sample orders, and accounts into the currently connected database.
    """
    if not request.user.is_authenticated or not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, "Access Denied: Admin authorization required to seed database.")
        return redirect('home')

    if request.method == 'POST':
        try:
            from django.core.management import call_command
            call_command('seed_data')
            messages.success(
                request,
                "✔ Demo dataset successfully seeded into the connected database! 13 Faculty products (IDs 101–113), categories, suppliers, warehouses, and demo accounts are ready."
            )
        except Exception as e:
            messages.error(request, f"❌ Failed to seed database: {str(e)}")

    return redirect('admin_dashboard')



@csrf_exempt
def user_dashboard_view(request):
    """
    Dedicated Customer Profile & Order History Dashboard for Logged-In Users
    """
    if not request.user.is_authenticated:
        messages.warning(request, "Please sign in to access your User Dashboard.")
        return redirect('login')

    # Locate or establish linked Customer profile
    customer = Customer.objects.filter(user=request.user).first()
    if not customer:
        customer = Customer.objects.filter(email=request.user.email).first()
        if customer and not customer.user:
            customer.user = request.user
            customer.save()
        elif not customer:
            customer = Customer.objects.create(
                user=request.user,
                full_name=request.user.get_full_name() or request.user.username,
                email=request.user.email or f"{request.user.username}@example.com",
                membership_level='Regular'
            )

    # Handle Profile Update Form Submit
    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        phone = request.POST.get('phone', '').strip()
        address = request.POST.get('address', '').strip()
        email = request.POST.get('email', '').strip()

        if full_name:
            customer.full_name = full_name
            request.user.first_name = full_name
        if phone:
            customer.phone = phone
        if address:
            customer.address = address
        if email:
            customer.email = email
            request.user.email = email

        customer.save()
        request.user.save()
        messages.success(request, "✔ Your profile details have been updated successfully!")
        return redirect('user_dashboard')

    # Fetch User's Orders
    user_orders = Order.objects.filter(customer=customer).prefetch_related('details__product', 'payment').order_by('-order_id')
    total_spent = user_orders.aggregate(total=Sum('total_amount'))['total'] or 0
    orders_count = user_orders.count()

    context = {
        'customer': customer,
        'user_orders': user_orders,
        'total_spent': total_spent,
        'orders_count': orders_count,
    }
    return render(request, 'dashboard/user_dashboard.html', context)


def place_order_view(request):
    """
    Handles Cart Checkout and Direct Product Order Placement.
    Supports both JSON AJAX payloads and standard Form POST submissions.
    Enforces Trigger 1 (Stock Validation), Trigger 2 (Payment Calculation), and ACID transactions.
    """
    if request.method != 'POST':
        return redirect('home')

    is_json = request.content_type == 'application/json' or request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if request.content_type == 'application/json':
        try:
            payload = json.loads(request.body.decode('utf-8'))
        except Exception as e:
            return JsonResponse({'success': False, 'message': f"Invalid JSON payload: {str(e)}"}, status=400)
    else:
        payload = request.POST

    # Extract items list
    items = []
    if isinstance(payload, dict) and 'items' in payload:
        raw_items = payload.get('items', [])
        for it in raw_items:
            try:
                p_id = int(it.get('product_id') or it.get('id'))
                qty = int(it.get('quantity') or 1)
                if qty > 0:
                    items.append({'product_id': p_id, 'quantity': qty})
            except (ValueError, TypeError):
                continue
    else:
        # Form post: single product or serialized cart
        cart_data = payload.get('cart_json')
        if cart_data:
            try:
                raw_items = json.loads(cart_data)
                for it in raw_items:
                    p_id = int(it.get('product_id') or it.get('id'))
                    qty = int(it.get('quantity') or 1)
                    if qty > 0:
                        items.append({'product_id': p_id, 'quantity': qty})
            except Exception:
                pass
        
        # Fallback to single product form parameters (e.g. quick buy)
        if not items and payload.get('product_id'):
            try:
                p_id = int(payload.get('product_id'))
                qty = int(payload.get('quantity', 1))
                if qty > 0:
                    items.append({'product_id': p_id, 'quantity': qty})
            except (ValueError, TypeError):
                pass

    if not items:
        if is_json:
            return JsonResponse({'success': False, 'message': 'Your shopping cart is empty.'}, status=400)
        messages.error(request, 'Your shopping cart is empty.')
        return redirect('home')

    # Resolve customer profile
    shipping_address = payload.get('shipping_address', '').strip()
    payment_method = payload.get('payment_method', 'Cash on Delivery').strip() or 'Cash on Delivery'
    
    customer = None
    if request.user.is_authenticated:
        customer = Customer.objects.filter(user=request.user).first()
        if not customer:
            customer = Customer.objects.filter(email=request.user.email).first()
            if customer and not customer.user:
                customer.user = request.user
                customer.save()
            elif not customer:
                customer = Customer.objects.create(
                    user=request.user,
                    full_name=request.user.get_full_name() or request.user.username,
                    email=request.user.email or f"{request.user.username}@example.com",
                    address=shipping_address or "Dhaka, Bangladesh",
                    membership_level='Regular'
                )
    else:
        # Guest customer resolution
        guest_email = payload.get('email', '').strip() or 'guest@example.com'
        guest_name = payload.get('full_name', '').strip() or 'Guest Customer'
        guest_phone = payload.get('phone', '').strip() or '+8801700000000'
        
        customer = Customer.objects.filter(email=guest_email).first()
        if not customer:
            customer = Customer.objects.create(
                full_name=guest_name,
                email=guest_email,
                phone=guest_phone,
                address=shipping_address or "Dhaka, Bangladesh",
                membership_level='Regular'
            )

    if not shipping_address:
        shipping_address = customer.address or "Dhaka, Bangladesh"

    # Transactional Order Creation
    try:
        with transaction.atomic():
            # 1. Pre-validate stock for each item
            products_to_order = []
            total_amount = 0.00
            for item in items:
                try:
                    product = Product.objects.select_for_update().get(product_id=item['product_id'])
                except Product.DoesNotExist:
                    raise ValidationError(f"Product ID #{item['product_id']} not found in catalog.")
                
                req_qty = item['quantity']
                if req_qty > product.stock_quantity:
                    raise ValidationError(
                        f"Insufficient stock for '{product.name}'. "
                        f"Requested {req_qty} units, but only {product.stock_quantity} available in database."
                    )
                
                item_subtotal = float(product.price) * req_qty
                total_amount += item_subtotal
                products_to_order.append({
                    'product': product,
                    'quantity': req_qty,
                    'unit_price': product.price,
                    'subtotal': item_subtotal
                })

            # 2. Create Order
            order = Order.objects.create(
                customer=customer,
                shipping_address=shipping_address,
                total_amount=total_amount,
                order_status='Pending'
            )

            # 3. Create OrderDetails & Deduct Inventory Stock
            for po in products_to_order:
                prod = po['product']
                qty = po['quantity']
                OrderDetail.objects.create(
                    order=order,
                    product=prod,
                    quantity=qty,
                    unit_price=po['unit_price'],
                    subtotal=po['subtotal']
                )
                prod.stock_quantity = max(0, prod.stock_quantity - qty)
                if prod.stock_quantity == 0:
                    prod.availability_status = "Out of Stock"
                prod.save()

            # 4. Trigger 2: Calculate Payment (Tax & Membership Discount)
            membership = (customer.membership_level or 'Regular').lower()
            discount_rates = {
                'platinum': 0.15,
                'gold': 0.10,
                'silver': 0.05,
                'regular': 0.00
            }
            discount_rate = discount_rates.get(membership, 0.00)
            tax_rate = 0.05  # 5% standard VAT

            tax = round(total_amount * tax_rate, 2)
            discount = round(total_amount * discount_rate, 2)
            payment_status = 'Pending' if payment_method.lower() in ('cash on delivery', 'cod') else 'Completed'

            payment = Payment.objects.create(
                order=order,
                amount=total_amount,
                tax=tax,
                discount=discount,
                payment_method=payment_method,
                payment_status=payment_status
            )

        success_msg = f"Order #{order.order_id} placed successfully! Total Paid: ${payment.final_amount:.2f}"
        if is_json:
            return JsonResponse({
                'success': True,
                'order_id': order.order_id,
                'total_amount': float(total_amount),
                'tax': float(tax),
                'discount': float(discount),
                'final_amount': float(payment.final_amount),
                'order_status': order.order_status,
                'message': success_msg
            })
        
        messages.success(request, success_msg)
        if request.user.is_authenticated:
            return redirect('user_dashboard')
        return redirect('home')

    except ValidationError as ve:
        err_msg = str(ve.messages[0]) if hasattr(ve, 'messages') else str(ve)
        if is_json:
            return JsonResponse({'success': False, 'message': err_msg}, status=400)
        messages.error(request, f"Order Placement Failed: {err_msg}")
        return redirect('home')
    except Exception as e:
        if is_json:
            return JsonResponse({'success': False, 'message': f"Order Failed: {str(e)}"}, status=500)
        messages.error(request, f"Unexpected error during order creation: {str(e)}")
        return redirect('home')


@csrf_exempt
def order_update_status_view(request, order_id):
    """
    Admin action to update order status dynamically
    """
    if not request.user.is_authenticated or not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, "Access Denied: Admin authorization required.")
        return redirect('home')

    if request.method == 'POST':
        order = get_object_or_404(Order, pk=order_id)
        new_status = request.POST.get('order_status', '').strip()
        valid_statuses = ['Pending', 'Processing', 'Shipped', 'Delivered', 'Cancelled']
        if new_status in valid_statuses:
            old_status = order.order_status
            order.order_status = new_status
            order.save()

            # If order status changed to Delivered, update payment status if pending
            if new_status == 'Delivered':
                payment = getattr(order, 'payment', None)
                if payment and payment.payment_status == 'Pending':
                    payment.payment_status = 'Completed'
                    payment.save()

            messages.success(request, f"✔ Order #{order.order_id} status updated from '{old_status}' to '{new_status}'.")
        else:
            messages.error(request, f"Invalid order status '{new_status}'.")

    next_url = request.POST.get('next', 'admin_dashboard')
    return redirect(next_url)


@csrf_exempt
def product_quick_stock_view(request, pk):
    """
    Quick inventory stock quantity update action for admin
    """
    if not request.user.is_authenticated or not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, "Access Denied: Admin authorization required.")
        return redirect('home')

    if request.method == 'POST':
        product = get_object_or_404(Product, pk=pk)
        new_stock = request.POST.get('stock_quantity', '0')
        try:
            stock_val = int(new_stock)
            product.stock_quantity = max(0, stock_val)
            product.availability_status = "In Stock" if product.stock_quantity > 0 else "Out of Stock"
            product.save()
            messages.success(request, f"✔ Product '{product.name}' [#{product.product_id}] stock updated to {product.stock_quantity} units.")
        except ValueError:
            messages.error(request, "Invalid stock quantity entered.")

    next_url = request.POST.get('next', 'admin_dashboard')
    return redirect(next_url)


# ==============================================================================
# HEADER SLIDER MANAGEMENT (ADMIN ACTIONS)
# ==============================================================================

@csrf_exempt
def admin_slider_list_view(request):
    """
    Admin View: Header Slider Management Portal
    """
    if not request.user.is_authenticated or not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, "Access Denied: Admin authorization required.")
        return redirect('login')

    slides = HeaderSlide.objects.all().order_by('display_order', '-created_at')
    products = Product.objects.all().order_by('name')
    
    context = {
        'slides': slides,
        'products': products,
    }
    return render(request, 'dashboard/admin_slider_list.html', context)


@csrf_exempt
def admin_slider_create_view(request):
    """
    Admin View: Add a new Header Slide with optional image upload / product linking
    """
    if not request.user.is_authenticated or not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, "Access Denied: Admin authorization required.")
        return redirect('login')

    products = Product.objects.all().order_by('name')

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        subtitle = request.POST.get('subtitle', '').strip()
        badge_text = request.POST.get('badge_text', 'CSE 303 Lab Project').strip()
        badge_color = request.POST.get('badge_color', 'primary').strip()
        button_text = request.POST.get('button_text', 'Explore Catalog').strip()
        button_url = request.POST.get('button_url', '#catalog-section').strip()
        secondary_button_text = request.POST.get('secondary_button_text', '').strip()
        secondary_button_url = request.POST.get('secondary_button_url', '').strip()
        image_url_input = request.POST.get('image_url', '').strip()
        product_id = request.POST.get('product_id', '')
        background_gradient = request.POST.get('background_gradient', 'linear-gradient(135deg, #0f172a 0%, #1e293b 100%)').strip()
        display_order = int(request.POST.get('display_order', 0))
        is_active = request.POST.get('is_active') == 'on' or request.POST.get('is_active') == 'true' or 'is_active' in request.POST

        if not title:
            messages.error(request, "Title is required for a header slide.")
            return redirect('admin_slider_create')

        linked_product = Product.objects.filter(pk=int(product_id)).first() if product_id and product_id.isdigit() else None

        slide = HeaderSlide.objects.create(
            title=title,
            subtitle=subtitle,
            badge_text=badge_text,
            badge_color=badge_color,
            button_text=button_text,
            button_url=button_url,
            secondary_button_text=secondary_button_text,
            secondary_button_url=secondary_button_url,
            image_url=image_url_input,
            product=linked_product,
            background_gradient=background_gradient,
            display_order=display_order,
            is_active=is_active
        )

        slide_image_file = request.FILES.get('slide_image')
        if slide_image_file:
            uploaded_url, msg = upload_slide_image_to_cloudinary(slide_image_file, slide.slide_id)
            if uploaded_url:
                slide.image_url = uploaded_url
                slide.save()

        messages.success(request, f"✔ Header slide '{slide.title}' successfully added!")
        return redirect('admin_slider_list')

    context = {
        'products': products,
    }
    return render(request, 'dashboard/admin_slider_form.html', context)


@csrf_exempt
def admin_slider_update_view(request, pk):
    """
    Admin View: Edit an existing Header Slide
    """
    if not request.user.is_authenticated or not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, "Access Denied: Admin authorization required.")
        return redirect('login')

    slide = get_object_or_404(HeaderSlide, pk=pk)
    products = Product.objects.all().order_by('name')

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        subtitle = request.POST.get('subtitle', '').strip()
        badge_text = request.POST.get('badge_text', '').strip()
        badge_color = request.POST.get('badge_color', 'primary').strip()
        button_text = request.POST.get('button_text', '').strip()
        button_url = request.POST.get('button_url', '').strip()
        secondary_button_text = request.POST.get('secondary_button_text', '').strip()
        secondary_button_url = request.POST.get('secondary_button_url', '').strip()
        image_url_input = request.POST.get('image_url', '').strip()
        product_id = request.POST.get('product_id', '')
        background_gradient = request.POST.get('background_gradient', '').strip()
        display_order = int(request.POST.get('display_order', 0))
        is_active = request.POST.get('is_active') == 'on' or request.POST.get('is_active') == 'true' or 'is_active' in request.POST

        if not title:
            messages.error(request, "Title is required.")
            return redirect('admin_slider_update', pk=pk)

        slide.title = title
        slide.subtitle = subtitle
        slide.badge_text = badge_text
        slide.badge_color = badge_color
        slide.button_text = button_text
        slide.button_url = button_url
        slide.secondary_button_text = secondary_button_text
        slide.secondary_button_url = secondary_button_url
        
        if image_url_input or not request.FILES.get('slide_image'):
            slide.image_url = image_url_input
            
        slide.product = Product.objects.filter(pk=int(product_id)).first() if product_id and product_id.isdigit() else None
        slide.background_gradient = background_gradient or slide.background_gradient
        slide.display_order = display_order
        slide.is_active = is_active

        slide_image_file = request.FILES.get('slide_image')
        if slide_image_file:
            uploaded_url, msg = upload_slide_image_to_cloudinary(slide_image_file, slide.slide_id)
            if uploaded_url:
                slide.image_url = uploaded_url

        slide.save()
        messages.success(request, f"✔ Header slide '{slide.title}' updated successfully!")
        return redirect('admin_slider_list')

    context = {
        'slide': slide,
        'products': products,
    }
    return render(request, 'dashboard/admin_slider_form.html', context)


@csrf_exempt
def admin_slider_delete_view(request, pk):
    """
    Admin View: Delete a Header Slide
    """
    if not request.user.is_authenticated or not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, "Access Denied: Admin authorization required.")
        return redirect('login')

    slide = get_object_or_404(HeaderSlide, pk=pk)
    if request.method == 'POST':
        title = slide.title
        slide.delete()
        messages.success(request, f"✔ Header slide '{title}' deleted.")
        return redirect('admin_slider_list')

    return redirect('admin_slider_list')


@csrf_exempt
def admin_slider_toggle_view(request, pk):
    """
    Admin View: Quick toggle slide active status
    """
    if not request.user.is_authenticated or not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, "Access Denied: Admin authorization required.")
        return redirect('login')

    slide = get_object_or_404(HeaderSlide, pk=pk)
    slide.is_active = not slide.is_active
    slide.save()
    status_str = "activated" if slide.is_active else "deactivated"
    messages.success(request, f"✔ Slide '{slide.title}' {status_str}.")
    return redirect('admin_slider_list')


# ==============================================================================
# PHASE 9: DJANGO ADMIN LOGIN & USER PERMISSIONS CONTROL SYSTEM
# ==============================================================================

def admin_user_permissions_view(request):
    """
    Admin Management View: Controls all Django admin login permissions,
    staff rights, superuser elevation, groups, and active statuses.
    """
    if not request.user.is_authenticated or not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, "Access Denied: Admin / Staff authorization required.")
        return redirect('login')

    users = User.objects.all().order_by('-is_superuser', '-is_staff', 'username')
    groups = Group.objects.all()

    # Calculate statistics
    total_users_count = users.count()
    staff_count = users.filter(is_staff=True).count()
    superuser_count = users.filter(is_superuser=True).count()
    customer_count = users.filter(is_staff=False, is_superuser=False).count()

    context = {
        'users': users,
        'groups': groups,
        'total_users_count': total_users_count,
        'staff_count': staff_count,
        'superuser_count': superuser_count,
        'customer_count': customer_count,
    }
    return render(request, 'dashboard/admin_user_permissions.html', context)


@csrf_exempt
def admin_user_permissions_update_view(request):
    """
    Admin Action: Update permissions, toggle staff/superuser status, or assign groups.
    """
    if not request.user.is_authenticated or not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, "Access Denied: Admin authorization required.")
        return redirect('login')

    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        role_action = request.POST.get('role_action')
        group_preset = request.POST.get('group_preset', '').strip()

        target_user = get_object_or_404(User, pk=user_id)

        # Safety Check: Prevent demoting the active logged in superuser if they are the only one
        if target_user.id == request.user.id and role_action in ['make_customer', 'toggle_active']:
            if User.objects.filter(is_superuser=True, is_active=True).count() <= 1 and target_user.is_superuser:
                messages.error(request, "Safety Warning: Cannot revoke permissions or deactivate the sole active Superuser account.")
                return redirect('admin_user_permissions')

        if role_action == 'make_staff':
            target_user.is_staff = True
            target_user.save()
            messages.success(request, f"✔ User '{target_user.username}' is now granted Staff Admin permissions (Can log into Django Admin and Staff Dashboard).")
        
        elif role_action == 'make_superuser':
            target_user.is_staff = True
            target_user.is_superuser = True
            target_user.save()
            messages.success(request, f"✔ User '{target_user.username}' is now granted Full Superuser Root permissions.")
        
        elif role_action == 'make_customer':
            target_user.is_staff = False
            target_user.is_superuser = False
            target_user.save()
            messages.info(request, f"ℹ User '{target_user.username}' permissions revoked. User is now a standard Customer.")
        
        elif role_action == 'toggle_active':
            target_user.is_active = not target_user.is_active
            target_user.save()
            state = "activated" if target_user.is_active else "deactivated"
            messages.warning(request, f"⚠ Account '{target_user.username}' has been {state}.")

        # Handle Group Presets
        if group_preset:
            group, _ = Group.objects.get_or_create(name=group_preset)
            target_user.groups.add(group)
            messages.success(request, f"✔ Added '{target_user.username}' to role group '{group_preset}'.")

        return redirect('admin_user_permissions')

    return redirect('admin_user_permissions')


@csrf_exempt
def admin_login_custom_view(request):
    """
    Custom CSRF-Exempt Django Admin Login Handler.
    Allows seamless authentication for Staff and Superusers into the Django Admin Console (/admin/)
    without CSRF cookie blocking in iframe previews and localhost environments.
    """
    next_url = request.GET.get('next') or request.POST.get('next') or '/admin/'

    # If user is already authenticated as staff, forward directly to destination
    if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser):
        return redirect(next_url)

    error_message = None

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_staff or user.is_superuser:
                login(request, user)
                messages.success(request, f"Welcome back Admin {user.username}! Signed into Django Admin Console.")
                return redirect(next_url)
            else:
                error_message = f"Account '{user.username}' is a Customer account without Staff Admin privileges."
        else:
            error_message = "Invalid administrator username or password. Please try again."

    return render(request, 'auth/admin_login.html', {
        'next_url': next_url,
        'error_message': error_message,
    })








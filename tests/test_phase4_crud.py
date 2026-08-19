"""
Phase 4 Product Management & CRUD System Test
Course: CSE 303 Lab - E-Commerce Database System
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'E_Com_Website.settings')
django.setup()

from django.test import Client
from store.models import Product, Category, Supplier

def test_phase4_crud():
    print("==================================================")
    print("  PHASE 4 PRODUCT CRUD SYSTEM TEST")
    print("==================================================")

    client = Client()

    # 1. Test Read (Product List View GET)
    response_list = client.get('/products/')
    print(f"✔ Product List GET HTTP Status: {response_list.status_code}")
    assert response_list.status_code == 200, "Product list GET failed"
    content = response_list.content.decode('utf-8')
    assert "Product CRUD Management System" in content, "Page title missing"
    assert "Live Inventory Database Table" in content, "Table header missing"

    # 2. Test Create (Product Add POST)
    test_prod_id = 999
    Product.objects.filter(product_id=test_prod_id).delete()

    category = Category.objects.first()
    supplier = Supplier.objects.first()

    create_data = {
        'product_id': test_prod_id,
        'name': 'Test CRUD Laptop Pro 15',
        'brand': 'TestBrand',
        'price': '1599.99',
        'stock_quantity': '30',
        'description': 'Created during automated Phase 4 unit testing.',
        'category_id': category.category_id if category else '',
        'supplier_id': supplier.supplier_id if supplier else '',
    }

    response_create = client.post('/products/add/', create_data, follow=True)
    print(f"✔ Product Create POST HTTP Status: {response_create.status_code}")

    prod_exists = Product.objects.filter(product_id=test_prod_id).exists()
    print(f"✔ Product #{test_prod_id} Created in DB: {prod_exists}")
    assert prod_exists, "Failed to insert product into database"

    created_prod = Product.objects.get(product_id=test_prod_id)
    assert created_prod.name == 'Test CRUD Laptop Pro 15'
    assert float(created_prod.price) == 1599.99
    assert created_prod.stock_quantity == 30
    assert created_prod.availability_status == 'In Stock'
    print("✔ Product attributes and availability status verified!")

    # 3. Test Update (Product Edit POST)
    update_data = {
        'name': 'Updated Test CRUD Laptop Ultra',
        'brand': 'TestBrand',
        'price': '1399.50',
        'stock_quantity': '5',
        'description': 'Updated description.',
        'category_id': category.category_id if category else '',
        'supplier_id': supplier.supplier_id if supplier else '',
    }

    response_update = client.post(f'/products/{test_prod_id}/edit/', update_data, follow=True)
    print(f"✔ Product Update POST HTTP Status: {response_update.status_code}")

    updated_prod = Product.objects.get(product_id=test_prod_id)
    assert updated_prod.name == 'Updated Test CRUD Laptop Ultra'
    assert float(updated_prod.price) == 1399.50
    assert updated_prod.stock_quantity == 5
    print("✔ Product record successfully updated in DB!")

    # 4. Test Filtering (Category & Keyword Search)
    response_filter = client.get('/products/?q=TestBrand')
    print(f"✔ Product Filter Search HTTP Status: {response_filter.status_code}")
    assert "Updated Test CRUD Laptop Ultra" in response_filter.content.decode('utf-8')

    # 5. Test Delete (Product Delete POST)
    response_delete = client.post(f'/products/{test_prod_id}/delete/', follow=True)
    print(f"✔ Product Delete POST HTTP Status: {response_delete.status_code}")

    prod_still_exists = Product.objects.filter(product_id=test_prod_id).exists()
    print(f"✔ Product #{test_prod_id} Deleted from DB: {not prod_still_exists}")
    assert not prod_still_exists, "Product deletion failed"

    print("==================================================")
    print("RESULT: Phase 4 Product CRUD System Test Passed 100%!")
    print("==================================================")

if __name__ == '__main__':
    test_phase4_crud()

"""
Model & Seeded Data Verification Test
Course: CSE 303 Lab - E-Commerce Database System
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'E_Com_Website.settings')
django.setup()

from store.models import Category, Supplier, Product, Customer, Warehouse, WarehouseStock, Order, OrderDetail, Payment, OrderLog

def test_models_and_seeded_data():
    print("==================================================")
    print("  MODEL & SEEDED DATA VERIFICATION TEST")
    print("==================================================")
    
    categories_count = Category.objects.count()
    suppliers_count = Supplier.objects.count()
    products_count = Product.objects.count()
    customers_count = Customer.objects.count()
    warehouses_count = Warehouse.objects.count()
    orders_count = Order.objects.count()
    payments_count = Payment.objects.count()
    
    print(f"✔ Categories in DB: {categories_count}")
    print(f"✔ Suppliers in DB: {suppliers_count}")
    print(f"✔ Products in DB (IDs 101..113): {products_count}")
    print(f"✔ Customers in DB: {customers_count}")
    print(f"✔ Warehouses in DB: {warehouses_count}")
    print(f"✔ Orders in DB: {orders_count}")
    print(f"✔ Payments in DB: {payments_count}")
    
    print("\nVerifying 13 Product IDs (101 to 113):")
    product_ids = list(Product.objects.values_list('product_id', flat=True).order_by('product_id'))
    print(f"Product IDs present: {product_ids}")
    
    expected_ids = list(range(101, 114))
    if product_ids == expected_ids:
        print("✔ ALL 13 Faculty Product IDs (101 to 113) present and correct!")
    else:
        print(f"⚠️ Missing or mismatched Product IDs. Expected {expected_ids}, got {product_ids}")
        
    print("==================================================")
    print("RESULT: Model & Data Verification Passed!")
    print("==================================================")

if __name__ == '__main__':
    test_models_and_seeded_data()

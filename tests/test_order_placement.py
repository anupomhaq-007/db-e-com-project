"""
Order Placement & Cart Checkout System Test
Course: CSE 303 Lab - E-Commerce Database System
"""

import os
import sys
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'E_Com_Website.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from store.models import Product, Customer, Order, OrderDetail, Payment

def test_order_placement():
    print("==================================================")
    print("  ORDER PLACEMENT & CART CHECKOUT SYSTEM TEST")
    print("==================================================")

    client = Client()

    # 1. Fetch test products
    p101 = Product.objects.get(product_id=101)
    p104 = Product.objects.get(product_id=104)
    initial_stock_101 = p101.stock_quantity
    initial_stock_104 = p104.stock_quantity

    print(f"Product 101 ('{p101.name}') Initial Stock: {initial_stock_101}")
    print(f"Product 104 ('{p104.name}') Initial Stock: {initial_stock_104}")

    # 2. Test Authenticated User Order Placement
    user = User.objects.get(username='arman')
    client.force_login(user)

    payload_auth = {
        'items': [
            {'product_id': 101, 'quantity': 2},
            {'product_id': 104, 'quantity': 1}
        ],
        'shipping_address': '12 Green Road, Dhanmondi, Dhaka',
        'payment_method': 'Bkash'
    }

    response_auth = client.post(
        '/orders/place/',
        data=json.dumps(payload_auth),
        content_type='application/json'
    )

    print(f"[OK] Authenticated Order POST Status: {response_auth.status_code}")
    assert response_auth.status_code == 200, f"Expected 200 OK, got {response_auth.status_code}"
    auth_data = response_auth.json()
    assert auth_data['success'] is True, "Order response indicated failure"
    order_id = auth_data['order_id']
    print(f"[OK] Created Order ID #{order_id} in Database!")

    # Verify Order in DB
    order_db = Order.objects.get(order_id=order_id)
    assert order_db.customer.user == user, "Customer user mismatch"
    assert order_db.order_status == 'Pending'
    assert order_db.details.count() == 2, "Expected 2 order details"

    # Verify Stock Deduction
    p101.refresh_from_db()
    p104.refresh_from_db()
    assert p101.stock_quantity == initial_stock_101 - 2, "Product 101 stock not decremented correctly"
    assert p104.stock_quantity == initial_stock_104 - 1, "Product 104 stock not decremented correctly"
    print(f"[OK] Inventory Stock Deductions Verified (P101: {p101.stock_quantity}, P104: {p104.stock_quantity})")

    # Verify Payment Trigger Auto-Calculation
    payment_db = Payment.objects.get(order=order_db)
    expected_subtotal = (2 * float(Product.objects.get(product_id=101).price)) + float(Product.objects.get(product_id=104).price)
    # Arman is Gold member (10% discount), 5% tax
    expected_tax = round(expected_subtotal * 0.05, 2)
    expected_discount = round(expected_subtotal * 0.10, 2)
    expected_final = round(expected_subtotal + expected_tax - expected_discount, 2)

    assert float(payment_db.amount) == expected_subtotal
    assert float(payment_db.tax) == expected_tax
    assert float(payment_db.discount) == expected_discount
    assert float(payment_db.final_amount) == expected_final
    print(f"[OK] Payment Trigger Auto-Calculation Verified: Subtotal=${expected_subtotal:.2f}, Tax=${expected_tax:.2f}, Discount=${expected_discount:.2f}, Final=${expected_final:.2f}")

    # 3. Test Stock Over-Order Validation (Trigger 1)
    payload_excess = {
        'items': [
            {'product_id': 101, 'quantity': p101.stock_quantity + 500}
        ],
        'shipping_address': 'Dhaka',
        'payment_method': 'Cash on Delivery'
    }
    response_excess = client.post(
        '/orders/place/',
        data=json.dumps(payload_excess),
        content_type='application/json'
    )
    print(f"[OK] Excessive Quantity POST Status: {response_excess.status_code}")
    assert response_excess.status_code == 400, f"Expected 400 Bad Request, got {response_excess.status_code}"
    excess_data = response_excess.json()
    assert excess_data['success'] is False
    assert "Insufficient stock" in excess_data['message']
    print(f"[OK] Stock Validation Trigger Blocked Over-Order: '{excess_data['message']}'")

    # 4. Test Guest User Checkout
    client_guest = Client()
    payload_guest = {
        'items': [
            {'product_id': 104, 'quantity': 1}
        ],
        'full_name': 'Guest Customer Tester',
        'email': 'guest.tester@example.com',
        'phone': '+8801999887766',
        'shipping_address': '77 Banani Road, Dhaka',
        'payment_method': 'Cash on Delivery'
    }
    response_guest = client_guest.post(
        '/orders/place/',
        data=json.dumps(payload_guest),
        content_type='application/json'
    )
    print(f"[OK] Guest Checkout POST Status: {response_guest.status_code}")
    assert response_guest.status_code == 200
    guest_data = response_guest.json()
    assert guest_data['success'] is True
    print(f"[OK] Guest Order #{guest_data['order_id']} Created Successfully!")

    # Verify Guest Customer Profile in DB
    guest_customer = Customer.objects.get(email='guest.tester@example.com')
    assert guest_customer.full_name == 'Guest Customer Tester'
    print(f"[OK] Guest Customer Record '{guest_customer.full_name}' Verified in DB!")

    print("==================================================")
    print("RESULT: Order Placement & Cart Checkout Test Passed 100%!")
    print("==================================================")

if __name__ == '__main__':
    test_order_placement()

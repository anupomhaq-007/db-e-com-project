"""
Phase 6 Database Triggers Bench Test (Task-2 Triggers a-c)
Course: CSE 303 Lab - E-Commerce Database System
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'E_Com_Website.settings')
django.setup()

from django.test import Client
from store.models import Product, Customer, Order, OrderDetail, Payment, OrderLog

def test_phase6_triggers():
    print("==================================================")
    print("  PHASE 6 DATABASE TRIGGERS BENCH TEST (a-c)")
    print("==================================================")

    client = Client()

    # 1. Test Triggers Portal GET
    response_get = client.get('/triggers/')
    print(f"✔ Triggers Portal GET HTTP Status: {response_get.status_code}")
    assert response_get.status_code == 200, "Triggers GET failed"
    content = response_get.content.decode('utf-8')
    assert "Database Triggers Test Bench" in content
    assert "Trigger 1: Stock Validation" in content
    assert "Trigger 2: Payment Auto-Calc" in content
    assert "Trigger 3: Order Deletion Audit" in content

    customer = Customer.objects.first()
    product = Product.objects.filter(stock_quantity__gt=5).first()
    assert customer is not None and product is not None, "Seed data missing for trigger tests"

    # 2. Test Trigger 1 (Stock Availability Validation - Valid Order)
    valid_payload = {
        'action': 'test_trigger1',
        'customer_id': customer.customer_id,
        'product_id': product.product_id,
        'quantity': 2,
    }
    response_t1_valid = client.post('/triggers/', valid_payload)
    print(f"✔ Trigger 1 Valid Order POST Status: {response_t1_valid.status_code}")
    assert response_t1_valid.status_code == 200
    res_t1_valid = response_t1_valid.content.decode('utf-8')
    assert "Trigger Passed" in res_t1_valid or "created for 2x" in res_t1_valid
    print("✔ Trigger 1 Valid Quantity Passed!")

    # 3. Test Trigger 1 (Stock Availability Validation - Excessive Quantity Blocked)
    excessive_payload = {
        'action': 'test_trigger1',
        'customer_id': customer.customer_id,
        'product_id': product.product_id,
        'quantity': 99999,  # Exceeds any stock_quantity
    }
    response_t1_block = client.post('/triggers/', excessive_payload)
    print(f"✔ Trigger 1 Excessive Quantity POST Status: {response_t1_block.status_code}")
    assert response_t1_block.status_code == 200
    res_t1_block = response_t1_block.content.decode('utf-8')
    assert "BLOCKED BY TRIGGER" in res_t1_block or "Insufficient stock" in res_t1_block
    print("✔ Trigger 1 Excessive Quantity Blocked Successfully by ValidationError Trigger!")

    # 4. Test Trigger 2 (Automated Payment Calculation)
    test_order = Order.objects.create(
        customer=customer,
        shipping_address=customer.address,
        total_amount=500.00,
        order_status='Pending'
    )

    t2_payload = {
        'action': 'test_trigger2',
        'order_id': test_order.order_id,
        'amount': '500.00',
        'tax': '25.00',
        'discount': '10.00',
        'payment_method': 'Credit Card',
    }
    response_t2 = client.post('/triggers/', t2_payload)
    print(f"✔ Trigger 2 Payment Auto-Calc POST Status: {response_t2.status_code}")
    assert response_t2.status_code == 200

    # Verify payment object in DB has final_amount = 500 + 25 - 10 = 515.00
    payment = Payment.objects.get(order=test_order)
    expected_final = 515.00
    print(f"✔ Payment DB Record Final Amount: ${payment.final_amount} (Expected: ${expected_final})")
    assert float(payment.final_amount) == expected_final, f"Trigger 2 calculation error: expected {expected_final}, got {payment.final_amount}"
    print("✔ Trigger 2 Final Amount Calculation Verified!")

    # 5. Test Trigger 3 (Order Deletion Audit Logger)
    order_to_delete = Order.objects.create(
        customer=customer,
        shipping_address="Audit Test Address",
        total_amount=750.00,
        order_status='Pending'
    )
    delete_order_id = order_to_delete.order_id

    t3_payload = {
        'action': 'test_trigger3',
        'order_id': delete_order_id,
    }
    response_t3 = client.post('/triggers/', t3_payload)
    print(f"✔ Trigger 3 Order Deletion Audit POST Status: {response_t3.status_code}")
    assert response_t3.status_code == 200

    # Verify Order was deleted from Order table
    order_exists = Order.objects.filter(order_id=delete_order_id).exists()
    assert not order_exists, "Order deletion failed"

    # Verify audit record exists in ORDER_LOG
    audit_log = OrderLog.objects.filter(order_id=delete_order_id).first()
    print(f"✔ Audit Log Entry Created for Deleted Order #{delete_order_id}: {audit_log}")
    assert audit_log is not None, "Trigger 3 failed to create ORDER_LOG entry"
    assert f"Order #{delete_order_id}" in audit_log.details
    print("✔ Trigger 3 Order Deletion Audit Logger Verified!")

    print("==================================================")
    print("RESULT: Phase 6 Database Triggers Test Passed 100%!")
    print("==================================================")

if __name__ == '__main__':
    test_phase6_triggers()

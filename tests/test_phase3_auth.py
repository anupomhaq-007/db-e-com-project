"""
Phase 3 User Authentication & Registration Test
Course: CSE 303 Lab - E-Commerce Database System
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'E_Com_Website.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from store.models import Customer

def test_phase3_auth():
    print("==================================================")
    print("  PHASE 3 AUTHENTICATION & ACCESS CONTROL TEST")
    print("==================================================")
    
    client = Client()

    # 1. Test Login Page GET
    response_login_get = client.get('/login/')
    print(f"✔ Login Page GET HTTP Status: {response_login_get.status_code}")
    assert response_login_get.status_code == 200, "Login GET failed"
    assert "User Sign In" in response_login_get.content.decode('utf-8')

    # 2. Test Registration Page GET
    response_reg_get = client.get('/register/')
    print(f"✔ Registration Page GET HTTP Status: {response_reg_get.status_code}")
    assert response_reg_get.status_code == 200, "Register GET failed"
    assert "Customer Registration" in response_reg_get.content.decode('utf-8')

    # 3. Test Registration POST (Create User & Customer Profile)
    test_user_data = {
        'username': 'test_student_22025214',
        'email': 'student22025214@example.com',
        'password': 'password123',
        'password_confirm': 'password123',
        'full_name': 'Test Student User',
        'phone': '+8801700002222',
        'address': 'Bashundhara R/A, Dhaka',
        'membership_level': 'Gold'
    }

    # Clean up if existing
    User.objects.filter(username=test_user_data['username']).delete()
    Customer.objects.filter(email=test_user_data['email']).delete()

    response_reg_post = client.post('/register/', test_user_data, follow=True)
    print(f"✔ Registration POST Redirect Status: {response_reg_post.status_code}")
    
    user_exists = User.objects.filter(username='test_student_22025214').exists()
    customer_exists = Customer.objects.filter(email='student22025214@example.com').exists()
    
    print(f"✔ User Created in DB: {user_exists}")
    print(f"✔ Customer Profile Created in DB: {customer_exists}")
    
    assert user_exists, "User registration failed to create User instance"
    assert customer_exists, "User registration failed to create Customer profile"
    
    customer = Customer.objects.get(email='student22025214@example.com')
    assert customer.membership_level == 'Gold', f"Expected Gold tier, got {customer.membership_level}"
    print(f"✔ Customer Membership Tier Verified: {customer.membership_level}")

    # 4. Test Logout
    response_logout = client.get('/logout/', follow=True)
    print(f"✔ Logout View HTTP Status: {response_logout.status_code}")

    # 5. Test Login POST with credentials
    login_data = {
        'username': 'test_student_22025214',
        'password': 'password123'
    }
    response_login_post = client.post('/login/', login_data, follow=True)
    print(f"✔ Login POST Response Status: {response_login_post.status_code}")
    
    # Check session
    assert '_auth_user_id' in client.session, "User session not authenticated after login"
    print("✔ User Session Successfully Authenticated!")

    print("==================================================")
    print("RESULT: Phase 3 Authentication Test Passed 100%!")
    print("==================================================")

if __name__ == '__main__':
    test_phase3_auth()

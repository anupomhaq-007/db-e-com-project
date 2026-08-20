"""
Phase 2 UI Component Rendering Test
Course: CSE 303 Lab - E-Commerce Database System
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import django
from django.test import Client

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'E_Com_Website.settings')
django.setup()

def test_phase2_ui():
    print("==================================================")
    print("  PHASE 2 FRONTEND UI COMPONENTS TEST")
    print("==================================================")
    
    client = Client()
    from django.contrib.auth.models import User
    user, _ = User.objects.get_or_create(username='testadmin', email='admin@test.com')
    client.force_login(user)
    
    response = client.get('/')
    
    print(f"✔ Homepage HTTP Status Code: {response.status_code}")
    assert response.status_code == 200, "Homepage failed to respond with 200 OK"
    
    content = response.content.decode('utf-8')
    
    # Check key Phase 2 HTML elements
    checks = [
        ("Base Layout & Bootstrap 5", "bootstrap.min.css"),
        ("Bootstrap Icons CDN", "bootstrap-icons.min.css"),
        ("Component 1: Navbar Brand", "E-Commerce DB Portal"),
        ("Component 1: Search Form", 'placeholder="Search product or brand..."'),
        ("Component 1: Cart Badge", 'id="cartCountBadge"'),
        ("Component 2: Hero Slider", 'id="heroCarousel"'),
        ("Component 3: Product Cards Grid", "product-card"),
        ("Component 3: Faculty Product IDs", "ID: 101"),
    ]
    
    all_passed = True
    for label, snippet in checks:
        if snippet in content:
            print(f"✔ {label} present in rendered DOM!")
        else:
            print(f"❌ {label} MISSING from rendered DOM!")
            all_passed = False
            
    print("==================================================")
    if all_passed:
        print("RESULT: Phase 2 Frontend UI Component Test Passed 100%!")
    else:
        print("RESULT: Some UI elements failed rendering checks.")
    print("==================================================")

if __name__ == '__main__':
    test_phase2_ui()

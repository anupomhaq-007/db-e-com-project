"""
Cloudinary Image Upload, Storage & Retrieval Test Suite
Course: CSE 303 Lab - E-Commerce Database System
"""

import os
import sys
import io
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'E_Com_Website.settings')
django.setup()

from django.test import Client
from django.core.files.uploadedfile import SimpleUploadedFile
from store.models import Product, Category, Supplier
from store.cloudinary_utils import upload_product_image_to_cloudinary, upload_slide_image_to_cloudinary

def test_cloudinary_and_media():
    print("==================================================")
    print("  CLOUDINARY & MEDIA UPLOAD/RETRIEVAL TEST SUITE")
    print("==================================================")
    
    cloudinary_url = os.environ.get('CLOUDINARY_URL', '').strip()
    print(f"CLOUDINARY_URL configured in env: {'YES (' + cloudinary_url.split('@')[-1] + ')' if cloudinary_url else 'NO (Local fallback active)'}")
    
    # 1. Test Dummy Image Creation
    # 1x1 pixel transparent PNG
    png_bytes = (
        b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06'
        b'\x00\x00\x00\x1f\x15c4\x00\x00\x00\rIDATx\x9cc`\x00\x00\x00\x02\x00\x01H'
        b'\xaf\xa4q\x00\x00\x00\x00IEND\xaeB`\x82'
    )
    uploaded_file = SimpleUploadedFile("sample_test_product.png", png_bytes, content_type="image/png")
    
    # 2. Test upload_product_image_to_cloudinary function directly
    print("\n1. Testing upload_product_image_to_cloudinary utility...")
    url, msg = upload_product_image_to_cloudinary(uploaded_file, product_id=987)
    print(f"✔ Upload Function Result URL: {url}")
    print(f"✔ Upload Function Message: {msg}")
    assert url is not None and len(url) > 0, "Image upload failed to produce a valid URL"
    
    # 3. Test Product Model get_image_url() with custom Cloudinary URL
    print("\n2. Testing Product model get_image_url() with Cloudinary URL...")
    test_cat = Category.objects.first()
    test_sup = Supplier.objects.first()
    
    cloudinary_sample_url = "https://res.cloudinary.com/demo/image/upload/v1611099999/ecommerce_products/laptop_sample.jpg"
    
    # Clean up prior test if exists
    Product.objects.filter(product_id=888).delete()
    prod = Product.objects.create(
        product_id=888,
        name="Cloudinary Test Ultrabook",
        brand="CloudTech",
        price=1299.99,
        stock_quantity=15,
        description="High-performance laptop with Cloudinary CDN media",
        availability_status="In Stock",
        image_url=cloudinary_sample_url,
        category=test_cat,
        supplier=test_sup
    )
    
    retrieved_url = prod.get_image_url()
    print(f"✔ Product #888 Stored Image URL: {prod.image_url}")
    print(f"✔ Product #888 get_image_url(): {retrieved_url}")
    assert retrieved_url == cloudinary_sample_url, "Retrieved image URL does not match stored Cloudinary URL"
    
    # 4. Test Image Upload via HTTP POST to product_create_view
    print("\n3. Testing Multipart Image Upload via product_create_view...")
    c = Client(HTTP_X_FORWARDED_PROTO='https')
    
    Product.objects.filter(product_id=889).delete()
    post_file = SimpleUploadedFile("web_upload_test.png", png_bytes, content_type="image/png")
    
    post_data = {
        'product_id': '889',
        'name': 'Cloudinary Form Upload Device',
        'brand': 'CloudBrand',
        'price': '499.50',
        'stock_quantity': '20',
        'description': 'Product created via multipart form upload',
        'category_id': str(test_cat.category_id) if test_cat else '',
        'supplier_id': str(test_sup.supplier_id) if test_sup else '',
        'product_image': post_file,
    }
    
    response = c.post('/products/add/', post_data, follow=True)
    print(f"✔ POST /products/add/ response status: {response.status_code}")
    assert response.status_code == 200
    
    created_prod = Product.objects.filter(product_id=889).first()
    assert created_prod is not None, "Product #889 was not found in DB"
    print(f"✔ Created Product in DB: {created_prod.name}")
    print(f"✔ Uploaded Product Image URL: {created_prod.image_url}")
    print(f"✔ Product get_image_url(): {created_prod.get_image_url()}")
    assert created_prod.image_url is not None and len(created_prod.image_url) > 0, "Uploaded image URL is empty"
    
    # 5. Test Image Retrieval and HTML Rendering on Frontend Pages
    print("\n4. Testing Image Retrieval in Frontend Templates...")
    
    # A. Homepage catalog grid
    res_home = c.get('/')
    assert res_home.status_code == 200
    content_home = res_home.content.decode('utf-8')
    assert "Cloudinary Form Upload Device" in content_home
    assert created_prod.get_image_url() in content_home
    print(f"✔ Homepage correctly displays product card with image URL: {created_prod.get_image_url()}")
    
    # B. CRUD Data Table
    res_list = c.get('/products/')
    assert res_list.status_code == 200
    content_list = res_list.content.decode('utf-8')
    assert "Cloudinary Form Upload Device" in content_list
    assert created_prod.get_image_url() in content_list
    print(f"✔ Product CRUD table correctly displays thumbnail and Cloudinary URL")
    
    # 6. Clean up temporary test products
    Product.objects.filter(product_id__in=[888, 889]).delete()
    print("\n✔ Cleaned up temporary test products from database.")
    
    print("==================================================")
    print("RESULT: Cloudinary & Media Upload/Retrieve Passed 100%!")
    print("==================================================")
    return True

if __name__ == '__main__':
    test_cloudinary_and_media()

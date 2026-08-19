import os
import django
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import User
from store.models import Category, Supplier, Product, Customer, Warehouse, WarehouseStock, Order, OrderDetail, Payment, OrderLog

class Command(BaseCommand):
    help = 'Seeds initial database records for CSE 303 Lab E-Commerce Management System'

    def handle(self, *args, **options):
        self.stdout.write("Seeding database initial dataset...")

        # 1. Categories
        c_tech, _ = Category.objects.get_or_create(name="Electronics & Gadgets", defaults={"description": "Laptops, Mobiles, and Smart Devices"})
        c_periph, _ = Category.objects.get_or_create(name="Computer Peripherals", defaults={"description": "Keyboards, Mice, Monitors, and Scanners"})
        c_net, _ = Category.objects.get_or_create(name="Networking & Storage", defaults={"description": "Routers, SSDs, and External Storage"})
        c_office, _ = Category.objects.get_or_create(name="Office Equipment", defaults={"description": "Printers, Webcams, and Stationeries"})

        # 2. Suppliers
        sup_tech, _ = Supplier.objects.get_or_create(
            company_name="TechPro Global Ltd.",
            defaults={"contact_person": "Alex Morgan", "phone": "+1-800-555-0199", "email": "contact@techpro.com", "address": "100 Tech Blvd, Silicon Valley, CA"}
        )
        sup_nexus, _ = Supplier.objects.get_or_create(
            company_name="Nexus Hardware Solutions",
            defaults={"contact_person": "Sarah Jenkins", "phone": "+1-800-555-0288", "email": "sales@nexushw.com", "address": "450 Innovation Way, Austin, TX"}
        )
        sup_apex, _ = Supplier.objects.get_or_create(
            company_name="Apex Logistics & Electronics",
            defaults={"contact_person": "David Miller", "phone": "+1-800-555-0377", "email": "support@apexel.com", "address": "88 Commerce St, Seattle, WA"}
        )

        # 3. Products (Product IDs 101 to 113)
        products_data = [
            (101, "Pro Ultrabook Laptop 15", "Dell", 12500.00, 45, "High-performance Intel i7 laptop with 16GB RAM", "In Stock", c_tech, sup_tech),
            (102, "Smartphone Galaxy Z", "Samsung", 8900.00, 60, "5G flagship smartphone with OLED display", "In Stock", c_tech, sup_nexus),
            (103, "LaserJet Pro Printer M404", "HP", 4200.00, 25, "Fast monochrome wireless laser printer", "In Stock", c_office, sup_apex),
            (104, "RGB Mechanical Gaming Keyboard", "Logitech", 1200.00, 120, "Tactile mechanical switches with custom lighting", "In Stock", c_periph, sup_tech),
            (105, "Wireless Ergonomic Mouse", "Logitech", 650.00, 150, "Precision optical sensor with dual-mode bluetooth", "In Stock", c_periph, sup_tech),
            (106, "4K UltraHD 27-inch Monitor", "LG", 6800.00, 30, "IPS panel with HDR10 support and USB-C hub", "In Stock", c_periph, sup_nexus),
            (107, "High-Speed Document Scanner", "Epson", 3100.00, 18, "Duplex color scanner for heavy office use", "In Stock", c_office, sup_apex),
            (108, "Dual-Band Wi-Fi 6 Router", "TP-Link", 1850.00, 80, "Gigabit wireless router with multi-device mesh support", "In Stock", c_net, sup_nexus),
            (109, "1TB NVMe M.2 Solid State Drive", "Samsung", 2400.00, 100, "High read/write speed PCIe Gen4 NVMe SSD", "In Stock", c_net, sup_tech),
            (110, "RTX 4070 Gaming Graphics Card", "ASUS", 14500.00, 12, "12GB GDDR6X ray-tracing desktop graphics card", "In Stock", c_tech, sup_nexus),
            (111, "Full HD 1080p Streaming Webcam", "Logitech", 950.00, 75, "Noise-reducing dual microphones and auto-focus lens", "In Stock", c_office, sup_tech),
            (112, "20,000mAh Fast Charge Power Bank", "Anker", 850.00, 110, "Dual USB-C Power Delivery portable power bank", "In Stock", c_tech, sup_apex),
            (113, "Fitness Tracker Smart Watch", "Apple", 7200.00, 40, "Always-on Retina display with heart rate and GPS tracking", "In Stock", c_tech, sup_tech),
        ]

        for p_id, name, brand, price, stock, desc, status, cat, sup in products_data:
            Product.objects.update_or_create(
                product_id=p_id,
                defaults={
                    "name": name,
                    "brand": brand,
                    "price": price,
                    "stock_quantity": stock,
                    "description": desc,
                    "availability_status": status,
                    "category": cat,
                    "supplier": sup,
                }
            )

        # 4. Warehouses
        w_main, _ = Warehouse.objects.get_or_create(warehouse_name="Central Megahub", defaults={"location": "Dhaka Industrial Zone", "storage_capacity": 10000})
        w_east, _ = Warehouse.objects.get_or_create(warehouse_name="Eastern Logistics Depot", defaults={"location": "Chittagong Port Area", "storage_capacity": 7500})
        w_north, _ = Warehouse.objects.get_or_create(warehouse_name="Northern Fulfillment Hub", defaults={"location": "Bogura Commerce Hub", "storage_capacity": 5000})

        # 5. WarehouseStock
        for p in Product.objects.all():
            WarehouseStock.objects.get_or_create(warehouse=w_main, product=p, defaults={"stock_quantity": int(p.stock_quantity * 0.6)})
            WarehouseStock.objects.get_or_create(warehouse=w_east, product=p, defaults={"stock_quantity": int(p.stock_quantity * 0.4)})

        # 6. Django Auth Users & Linked Customers
        # Create Superusers
        admin_user, _ = User.objects.get_or_create(
            username="admin",
            defaults={"email": "admin@ecommerce.com", "first_name": "System Administrator", "is_staff": True, "is_superuser": True}
        )
        admin_user.set_password("admin123")
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.save()

        test_admin, _ = User.objects.get_or_create(
            username="testadmin",
            defaults={"email": "admin@test.com", "first_name": "Test Admin", "is_staff": True, "is_superuser": True}
        )
        test_admin.set_password("admin123")
        test_admin.is_staff = True
        test_admin.is_superuser = True
        test_admin.save()

        # Create Customer Users & Linked Profiles
        cust_data = [
            ("arman", "arman123", "Arman Rahman", "arman.rahman@example.com", "+8801711223344", "12 Green Road, Dhaka", "Gold"),
            ("salman", "salman123", "Salman Khan", "salman.khan@example.com", "+8801811223344", "45 Park Street, Chittagong", "Platinum"),
            ("norman", "norman123", "Norman Bates", "norman.bates@example.com", "+8801911223344", "88 Motel Way, Sylhet", "Regular"),
            ("sarah", "sarah123", "Sarah Connor", "sarah.connor@example.com", "+8801511223344", "102 Cyber Lane, Dhaka", "Silver"),
            ("john", "john123", "John Doe", "john.doe@example.com", "+8801611223344", "15 Main Street, Khulna", "Regular"),
        ]

        customers = []
        for username, password, name, email, phone, addr, level in cust_data:
            u, _ = User.objects.get_or_create(
                username=username,
                defaults={"email": email, "first_name": name}
            )
            u.set_password(password)
            u.save()

            c, _ = Customer.objects.get_or_create(
                email=email,
                defaults={"user": u, "full_name": name, "phone": phone, "address": addr, "membership_level": level}
            )
            if not c.user:
                c.user = u
                c.save()
            customers.append(c)

        # 7. Sample Orders & Payments
        p101 = Product.objects.get(product_id=101)
        p102 = Product.objects.get(product_id=102)
        p104 = Product.objects.get(product_id=104)
        p108 = Product.objects.get(product_id=108)

        # Order 1 (Completed)
        o1 = Order.objects.filter(customer=customers[0]).first()
        if not o1:
            o1 = Order.objects.create(
                customer=customers[0],
                order_status="Delivered",
                shipping_address=customers[0].address,
                total_amount=13700.00
            )
        OrderDetail.objects.get_or_create(order=o1, product=p101, defaults={"quantity": 1, "unit_price": p101.price, "subtotal": p101.price})
        OrderDetail.objects.get_or_create(order=o1, product=p104, defaults={"quantity": 1, "unit_price": p104.price, "subtotal": p104.price})
        Payment.objects.get_or_create(order=o1, defaults={"amount": 13700.00, "tax": 685.00, "discount": 500.00, "payment_method": "Credit Card", "payment_status": "Completed"})

        # Order 2 (Pending)
        o2 = Order.objects.filter(customer=customers[1]).first()
        if not o2:
            o2 = Order.objects.create(
                customer=customers[1],
                order_status="Pending",
                shipping_address=customers[1].address,
                total_amount=8900.00
            )
        OrderDetail.objects.get_or_create(order=o2, product=p102, defaults={"quantity": 1, "unit_price": p102.price, "subtotal": p102.price})
        Payment.objects.get_or_create(order=o2, defaults={"amount": o2.total_amount, "tax": 445.00, "discount": 200.00, "payment_method": "Bkash", "payment_status": "Pending"})

        # Order 3 (Pending)
        o3 = Order.objects.filter(customer=customers[3]).first()
        if not o3:
            o3 = Order.objects.create(
                customer=customers[3],
                order_status="Pending",
                shipping_address=customers[3].address,
                total_amount=1850.00
            )
        OrderDetail.objects.get_or_create(order=o3, product=p108, defaults={"quantity": 1, "unit_price": p108.price, "subtotal": p108.price})
        Payment.objects.get_or_create(order=o3, defaults={"amount": o3.total_amount, "tax": 92.50, "discount": 0.00, "payment_method": "Cash on Delivery", "payment_status": "Pending"})

        self.stdout.write(self.style.SUCCESS("✔ Successfully seeded initial database dataset into Neon PostgreSQL!"))

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db.models.signals import pre_delete
from django.dispatch import receiver

class Category(models.Model):
    category_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} (ID: {self.category_id})"

    class Meta:
        verbose_name_plural = "Categories"


class Supplier(models.Model):
    supplier_id = models.AutoField(primary_key=True)
    company_name = models.CharField(max_length=150)
    contact_person = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    address = models.TextField()

    def __str__(self):
        return self.company_name


class Product(models.Model):
    product_id = models.IntegerField(primary_key=True, help_text="Custom Product ID (e.g. 101-113)")
    name = models.CharField(max_length=150)
    brand = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.IntegerField(default=0)
    description = models.TextField(blank=True, null=True)
    availability_status = models.CharField(max_length=50, default="In Stock")
    image_url = models.CharField(max_length=500, blank=True, null=True, help_text="Cloudinary CDN or image URL")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="products")
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True, related_name="products")

    def get_image_url(self):
        """
        Returns the Cloudinary CDN image URL if stored, otherwise a high quality default placeholder.
        """
        if self.image_url and self.image_url.strip():
            return self.image_url.strip()
        
        # Category-based default product image placeholders
        cat_name = self.category.name.lower() if self.category else ""
        if "laptop" in cat_name or "laptop" in self.name.lower():
            return "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?auto=format&fit=crop&w=600&q=80"
        elif "mobile" in cat_name or "phone" in cat_name or "phone" in self.name.lower():
            return "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?auto=format&fit=crop&w=600&q=80"
        elif "monitor" in cat_name or "display" in cat_name or "screen" in self.name.lower():
            return "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?auto=format&fit=crop&w=600&q=80"
        elif "peripheral" in cat_name or "keyboard" in self.name.lower() or "mouse" in self.name.lower():
            return "https://images.unsplash.com/photo-1587829741301-dc798b83add3?auto=format&fit=crop&w=600&q=80"
        else:
            return "https://images.unsplash.com/photo-1526738549149-8e07eca6c147?auto=format&fit=crop&w=600&q=80"

    def __str__(self):
        return f"[{self.product_id}] {self.name} - ${self.price}"


class Customer(models.Model):
    MEMBERSHIP_CHOICES = [
        ('Regular', 'Regular'),
        ('Silver', 'Silver'),
        ('Gold', 'Gold'),
        ('Platinum', 'Platinum'),
    ]
    customer_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name="customer_profile")
    full_name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    registration_date = models.DateField(default=timezone.now)
    membership_level = models.CharField(max_length=20, choices=MEMBERSHIP_CHOICES, default='Regular')

    def __str__(self):
        return f"{self.full_name} ({self.membership_level})"


class Warehouse(models.Model):
    warehouse_id = models.AutoField(primary_key=True)
    warehouse_name = models.CharField(max_length=100)
    location = models.CharField(max_length=150)
    storage_capacity = models.IntegerField(help_text="Capacity in units")

    def __str__(self):
        return f"{self.warehouse_name} ({self.location})"


class WarehouseStock(models.Model):
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name="stocks")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="warehouse_stocks")
    stock_quantity = models.IntegerField(default=0)

    class Meta:
        unique_together = ('warehouse', 'product')

    def __str__(self):
        return f"{self.warehouse.warehouse_name} - {self.product.name}: {self.stock_quantity}"


class Order(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    ]
    order_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="orders")
    order_date = models.DateTimeField(default=timezone.now)
    order_status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='Pending')
    shipping_address = models.TextField()
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Order #{self.order_id} - {self.customer.full_name} (${self.total_amount})"


class OrderDetail(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="details")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="order_details")
    quantity = models.IntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)

    def clean(self):
        if self.product and self.quantity > self.product.stock_quantity:
            raise ValidationError(
                f"Trigger Exception: Insufficient stock for '{self.product.name}'. "
                f"Requested quantity ({self.quantity}) exceeds available stock ({self.product.stock_quantity})."
            )

    def save(self, *args, **kwargs):
        if not self.unit_price and self.product:
            self.unit_price = self.product.price
        if self.unit_price and self.quantity:
            self.subtotal = self.unit_price * self.quantity
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order #{self.order.order_id} Item: {self.product.name} (x{self.quantity})"


class Payment(models.Model):
    payment_id = models.AutoField(primary_key=True)
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="payment")
    payment_date = models.DateTimeField(default=timezone.now)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    final_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    payment_method = models.CharField(max_length=50, default="Credit Card")
    payment_status = models.CharField(max_length=30, default="Completed")

    def save(self, *args, **kwargs):
        self.final_amount = self.amount + self.tax - self.discount
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Payment #{self.payment_id} for Order #{self.order.order_id}: ${self.final_amount}"


class HeaderSlide(models.Model):
    slide_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    subtitle = models.TextField(blank=True, null=True)
    badge_text = models.CharField(max_length=100, default="CSE 303 Lab Project")
    badge_color = models.CharField(max_length=50, default="primary", help_text="Bootstrap badge color e.g. primary, warning, info, success, danger")
    button_text = models.CharField(max_length=100, default="Explore Products")
    button_url = models.CharField(max_length=255, default="#catalog-section")
    secondary_button_text = models.CharField(max_length=100, blank=True, null=True)
    secondary_button_url = models.CharField(max_length=255, blank=True, null=True)
    image_url = models.CharField(max_length=500, blank=True, null=True, help_text="Image URL or uploaded photo URL")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, related_name="slides", help_text="Optional linked product")
    background_gradient = models.CharField(max_length=255, default="linear-gradient(135deg, #0f172a 0%, #1e293b 100%)")
    display_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    def get_image_url(self):
        if self.image_url and self.image_url.strip():
            return self.image_url.strip()
        if self.product:
            return self.product.get_image_url()
        return ""

    def __str__(self):
        return f"Slide #{self.slide_id}: {self.title}"

    class Meta:
        ordering = ['display_order', '-created_at']


class OrderLog(models.Model):
    log_id = models.AutoField(primary_key=True)
    order_id = models.IntegerField()
    deletion_timestamp = models.DateTimeField(default=timezone.now)
    details = models.TextField()

    def __str__(self):
        return f"Audit Log #{self.log_id} - Deleted Order #{self.order_id} at {self.deletion_timestamp}"


@receiver(pre_delete, sender=Order)
def log_order_deletion_audit(sender, instance, **kwargs):
    cust_name = instance.customer.full_name if instance.customer else "Unknown Customer"
    OrderLog.objects.create(
        order_id=instance.order_id,
        deletion_timestamp=timezone.now(),
        details=f"TRIGGER AUDIT LOG: Order #{instance.order_id} (Customer: {cust_name}, Total: ${instance.total_amount}, Status: {instance.order_status}) was deleted."
    )

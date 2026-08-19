from django.contrib import admin
from django.contrib.auth.models import User, Group, Permission
from .models import (
    Category, Supplier, Product, Customer,
    Warehouse, WarehouseStock, Order, OrderDetail,
    Payment, OrderLog, HeaderSlide
)

# Configure Django Admin Interface Branding & Control Titles
admin.site.site_header = "E-Commerce Database Administration & Control"
admin.site.site_title = "E-Com Admin Portal"
admin.site.index_title = "System Management & Database Permissions Control"


@admin.register(HeaderSlide)
class HeaderSlideAdmin(admin.ModelAdmin):
    list_display = ('slide_id', 'title', 'badge_text', 'display_order', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'subtitle', 'badge_text')
    list_editable = ('display_order', 'is_active')
    ordering = ('display_order', '-created_at')
    fieldsets = (
        ('Slide Content', {
            'fields': ('title', 'subtitle', 'badge_text', 'badge_color')
        }),
        ('Buttons & Links', {
            'fields': ('button_text', 'button_url', 'secondary_button_text', 'secondary_button_url')
        }),
        ('Media & Association', {
            'fields': ('image_url', 'product', 'background_gradient')
        }),
        ('Visibility & Ordering', {
            'fields': ('display_order', 'is_active')
        }),
    )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('category_id', 'name', 'description')
    search_fields = ('name', 'description')
    ordering = ('category_id',)


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('supplier_id', 'company_name', 'contact_person', 'phone', 'email', 'address')
    search_fields = ('company_name', 'contact_person', 'email', 'phone', 'address')
    ordering = ('supplier_id',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_id', 'name', 'brand', 'category', 'supplier', 'price', 'stock_quantity', 'availability_status')
    list_filter = ('category', 'supplier', 'availability_status')
    search_fields = ('name', 'brand', 'description')
    list_editable = ('price', 'stock_quantity', 'availability_status')
    ordering = ('product_id',)


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('customer_id', 'full_name', 'email', 'phone', 'membership_level', 'registration_date')
    list_filter = ('membership_level', 'registration_date')
    search_fields = ('full_name', 'email', 'phone', 'address')
    ordering = ('customer_id',)


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ('warehouse_id', 'warehouse_name', 'location', 'storage_capacity')
    search_fields = ('warehouse_name', 'location')
    ordering = ('warehouse_id',)


@admin.register(WarehouseStock)
class WarehouseStockAdmin(admin.ModelAdmin):
    list_display = ('id', 'warehouse', 'product', 'stock_quantity')
    list_filter = ('warehouse', 'product')
    search_fields = ('warehouse__warehouse_name', 'product__name')
    list_editable = ('stock_quantity',)
    ordering = ('warehouse', 'product')


class OrderDetailInline(admin.TabularInline):
    model = OrderDetail
    extra = 1
    fields = ('product', 'quantity', 'unit_price', 'subtotal')
    readonly_fields = ('subtotal',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'customer', 'order_date', 'total_amount', 'order_status', 'shipping_address')
    list_filter = ('order_status', 'order_date')
    search_fields = ('order_id', 'customer__full_name', 'customer__email', 'shipping_address')
    list_editable = ('order_status',)
    inlines = [OrderDetailInline]
    ordering = ('-order_date', '-order_id')


@admin.register(OrderDetail)
class OrderDetailAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'product', 'quantity', 'unit_price', 'subtotal')
    list_filter = ('product',)
    search_fields = ('order__order_id', 'product__name')
    ordering = ('order', 'id')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('payment_id', 'order', 'payment_date', 'payment_method', 'amount', 'tax', 'discount', 'final_amount', 'payment_status')
    list_filter = ('payment_method', 'payment_status', 'payment_date')
    search_fields = ('payment_id', 'order__order_id')
    list_editable = ('payment_status',)
    ordering = ('-payment_date', '-payment_id')


@admin.register(OrderLog)
class OrderLogAdmin(admin.ModelAdmin):
    list_display = ('log_id', 'order_id', 'deletion_timestamp', 'details')
    list_filter = ('deletion_timestamp',)
    search_fields = ('order_id', 'details')
    readonly_fields = ('log_id', 'order_id', 'deletion_timestamp', 'details')
    ordering = ('-deletion_timestamp',)

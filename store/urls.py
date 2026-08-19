from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboards & Management (Phase 8 Extensions)
    path('dashboard/admin/', views.admin_dashboard_view, name='admin_dashboard'),
    path('dashboard/admin/reseed/', views.admin_reseed_data_view, name='admin_reseed_data'),
    path('dashboard/admin/slides/', views.admin_slider_list_view, name='admin_slider_list'),
    path('dashboard/admin/slides/add/', views.admin_slider_create_view, name='admin_slider_create'),
    path('dashboard/admin/slides/<int:pk>/edit/', views.admin_slider_update_view, name='admin_slider_update'),
    path('dashboard/admin/slides/<int:pk>/delete/', views.admin_slider_delete_view, name='admin_slider_delete'),
    path('dashboard/admin/slides/<int:pk>/toggle/', views.admin_slider_toggle_view, name='admin_slider_toggle'),
    path('dashboard/admin/permissions/', views.admin_user_permissions_view, name='admin_user_permissions'),
    path('dashboard/admin/permissions/update/', views.admin_user_permissions_update_view, name='admin_user_permissions_update'),
    path('dashboard/user/', views.user_dashboard_view, name='user_dashboard'),

    path('orders/place/', views.place_order_view, name='place_order'),
    path('checkout/', views.place_order_view, name='checkout'),
    path('orders/<int:order_id>/update-status/', views.order_update_status_view, name='order_update_status'),
    path('products/<int:pk>/quick-stock/', views.product_quick_stock_view, name='product_quick_stock'),

    # Phase 4 Product CRUD System
    path('products/', views.product_list_view, name='product_list'),
    path('products/add/', views.product_create_view, name='product_create'),
    path('products/<int:pk>/edit/', views.product_update_view, name='product_update'),
    path('products/<int:pk>/delete/', views.product_delete_view, name='product_delete'),
    
    # Phase 5 Analytical SQL Queries Center
    path('queries/', views.queries_view, name='queries'),

    # Phase 6 Database Triggers Bench
    path('triggers/', views.triggers_view, name='triggers'),

    # Phase 7 Advanced DBMS Capabilities, Reporting & Visualizers
    path('report/', views.report_view, name='report'),
]


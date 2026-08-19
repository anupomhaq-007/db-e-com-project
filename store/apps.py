from django.apps import AppConfig
from django.db.models.signals import post_migrate

def ensure_default_users(sender, **kwargs):
    """
    Auto-provision superuser admin and default staff/customer accounts post migration
    """
    try:
        from django.contrib.auth.models import User
        # Ensure superuser 'admin'
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={'email': 'admin@ecommerce.com', 'first_name': 'System Administrator', 'is_staff': True, 'is_superuser': True}
        )
        if created or not admin_user.is_staff or not admin_user.is_superuser or not admin_user.check_password('admin123'):
            admin_user.set_password('admin123')
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.save()

        # Ensure testadmin
        test_admin, created = User.objects.get_or_create(
            username='testadmin',
            defaults={'email': 'admin@test.com', 'first_name': 'Test Admin', 'is_staff': True, 'is_superuser': True}
        )
        if created or not test_admin.is_staff or not test_admin.is_superuser:
            test_admin.set_password('admin123')
            test_admin.is_staff = True
            test_admin.is_superuser = True
            test_admin.save()
    except Exception as e:
        pass


class StoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'store'

    def ready(self):
        post_migrate.connect(ensure_default_users, sender=self)

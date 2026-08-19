import os
from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    help = 'Displays current environment variables, Secret Key, and Database settings.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("=" * 60))
        self.stdout.write(self.style.SUCCESS("  E-COMMERCE SYSTEM ENVIRONMENT & SETTINGS AUDIT"))
        self.stdout.write(self.style.SUCCESS("=" * 60))

        # 1. Secret Key
        raw_secret = getattr(settings, 'SECRET_KEY', '')
        is_env_secret = 'SECRET_KEY' in os.environ
        if len(raw_secret) > 10:
            masked_secret = raw_secret[:6] + "..." + raw_secret[-4:]
        else:
            masked_secret = "***"

        self.stdout.write(f"- SECRET_KEY (In Use) : {raw_secret}")
        self.stdout.write(f"- SECRET_KEY Source   : {'Environment Variable (os.environ)' if is_env_secret else 'Django Default Fallback'}")

        # 2. Database Connection
        db_conf = settings.DATABASES.get('default', {})
        db_engine = db_conf.get('ENGINE', '')
        db_name = db_conf.get('NAME', '')
        db_host = db_conf.get('HOST', 'localhost')
        db_user = db_conf.get('USER', '')
        raw_db_url = os.environ.get('DATABASE_URL', '')

        self.stdout.write(f"\n- DATABASE_ENGINE     : {db_engine}")
        self.stdout.write(f"- DATABASE_NAME       : {db_name}")
        self.stdout.write(f"- DATABASE_HOST       : {db_host}")
        self.stdout.write(f"- DATABASE_USER       : {db_user}")
        if raw_db_url:
            # Mask credentials in output
            if '@' in raw_db_url:
                db_host_part = raw_db_url.split('@')[-1]
                self.stdout.write(f"- DATABASE_URL (Host) : ...@{db_host_part}")
            else:
                self.stdout.write("- DATABASE_URL        : Configured")
        else:
            self.stdout.write("- DATABASE_URL        : Not set (Using local SQLite database)")

        # 3. Cloudinary Configuration
        raw_cloud_url = os.environ.get('CLOUDINARY_URL', '').strip()
        if raw_cloud_url:
            cloud_name = raw_cloud_url.split('@')[-1] if '@' in raw_cloud_url else 'Configured'
            self.stdout.write(f"\n- CLOUDINARY_URL      : Active (Cloud: {cloud_name})")
        else:
            self.stdout.write("\n- CLOUDINARY_URL      : Not set (Using local /media/ filesystem fallback)")

        # 4. Security Origins
        self.stdout.write(f"\n- ALLOWED_HOSTS       : {settings.ALLOWED_HOSTS}")
        self.stdout.write(f"- CSRF_TRUSTED_ORIGINS: {settings.CSRF_TRUSTED_ORIGINS}")

        self.stdout.write(self.style.SUCCESS("=" * 60))

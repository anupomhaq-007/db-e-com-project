"""
Django System Setup & Configuration Test
Course: CSE 303 Lab - E-Commerce Database System
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import django
from django.core.management import call_command

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'E_Com_Website.settings')
django.setup()

def test_django_environment():
    print("==================================================")
    print("  DJANGO ENVIRONMENT & CONFIGURATION TEST")
    print("==================================================")
    
    from django.conf import settings
    
    print(f"✔ DJANGO_SETTINGS_MODULE: {os.environ.get('DJANGO_SETTINGS_MODULE')}")
    print(f"✔ DEBUG mode: {settings.DEBUG}")
    print(f"✔ ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
    print(f"✔ CSRF_TRUSTED_ORIGINS: {settings.CSRF_TRUSTED_ORIGINS}")
    print(f"✔ Templates Directory Configured: {settings.TEMPLATES[0]['DIRS']}")
    print(f"✔ Static Files Directory Configured: {settings.STATICFILES_DIRS}")
    
    print("\nRunning Django System Check (manage.py check)...")
    try:
        call_command('check')
        print("✔ Django System Check passed with 0 issues!")
    except Exception as e:
        print(f"❌ System Check Failed: {e}")
        return False

    print("==================================================")
    print("RESULT: Django Setup Test Passed 100%!")
    print("==================================================")
    return True

if __name__ == '__main__':
    test_django_environment()

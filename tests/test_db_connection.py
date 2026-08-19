"""
Neon PostgreSQL Database Connection Test
Course: CSE 303 Lab - E-Commerce Database System
"""

import os
import sys

# Add parent directory to path so Django settings can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'E_Com_Website.settings')
django.setup()

from django.db import connection

def test_neon_connection():
    db_url = os.environ.get('DATABASE_URL')
    print("==================================================")
    print("  NEON POSTGRESQL DATABASE CONNECTION TEST")
    print("==================================================")
    print(f"DATABASE_URL configured: {'YES' if db_url else 'NO'}")
    
    try:
        connection.ensure_connection()
        print("✔ Database connection successfully established!")
        
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            print(f"✔ Engine Version: {version}")
            
            cursor.execute("SELECT current_database(), current_user;")
            db_name, db_user = cursor.fetchone()
            print(f"✔ Connected DB: '{db_name}' as User: '{db_user}'")
            
            # Check migrations table
            cursor.execute("SELECT COUNT(*) FROM django_migrations;")
            migration_count = cursor.fetchone()[0]
            print(f"✔ Migrations applied in Neon DB: {migration_count}")
            
        print("==================================================")
        print("RESULT: Neon PostgreSQL Database Connection Passed 100%!")
        print("==================================================")
        return True
    except Exception as e:
        print(f"❌ Connection Failed: {e}")
        print("==================================================")
        return False

if __name__ == '__main__':
    test_neon_connection()

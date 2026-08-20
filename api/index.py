import os
import sys

# Ensure root directory is in sys.path for Vercel Serverless Function engine
path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if path not in sys.path:
    sys.path.insert(0, path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'E_Com_Website.settings')

from django.core.wsgi import get_wsgi_application

app = get_wsgi_application()

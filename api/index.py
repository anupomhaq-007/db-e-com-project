import os
import sys

# Ensure the project root directory is in the Python search path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'E_Com_Website.settings')

from django.core.wsgi import get_wsgi_application

# Vercel Serverless Function entrypoint
app = get_wsgi_application()

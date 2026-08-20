import os
import sys

# Ensure root directory is in sys.path for Vercel Serverless Function engine
path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if path not in sys.path:
    sys.path.insert(0, path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'E_Com_Website.settings')

import django
django.setup()

# Auto-apply database migrations on cold boot to ensure Neon PostgreSQL schema is synced
try:
    from django.core.management import call_command
    call_command('migrate', interactive=False)
except Exception as e:
    print(f"[Vercel Migration Notice]: {e}", flush=True)

from django.core.wsgi import get_wsgi_application

_application = get_wsgi_application()

def app(environ, start_response):
    """
    Vercel WSGI Wrapper
    Normalizes PATH_INFO if Vercel forwards requests with '/api/index.py' prefix.
    """
    path_info = environ.get('PATH_INFO', '')
    if path_info.startswith('/api/index.py'):
        cleaned_path = path_info.replace('/api/index.py', '', 1)
        environ['PATH_INFO'] = cleaned_path if cleaned_path else '/'

    return _application(environ, start_response)

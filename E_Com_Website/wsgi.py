import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'E_Com_Website.settings')

application = get_wsgi_application()

# Alias for Vercel / serverless WSGI entrypoint detection
app = application

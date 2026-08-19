import os
import sys

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'E_Com_Website.settings')

    # Detect port from environment variable (Cloud Run sets PORT, e.g. 8080) or fallback to 3000
    port = os.environ.get('PORT', '3000')
    host = os.environ.get('HOST', '0.0.0.0')

    # Parse command-line args for --port / -p and --host / -h
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] in ('--port', '-p') and i + 1 < len(args):
            port = args[i + 1]
            i += 2
        elif args[i].startswith('--port='):
            port = args[i].split('=', 1)[1]
            i += 1
        elif args[i] in ('--host', '-h') and i + 1 < len(args):
            host = args[i + 1]
            i += 2
        elif args[i].startswith('--host='):
            host = args[i].split('=', 1)[1]
            i += 1
        else:
            i += 1

    bind_address = f"{host}:{port}"
    print(f"[Django Server] Initializing on {bind_address} (PORT={port}, HOST={host})...", flush=True)

    # Initialize Django
    import django
    django.setup()

    # Ensure database migrations are applied
    try:
        from django.core.management import call_command
        print("[Django Server] Checking and applying database migrations...", flush=True)
        call_command('migrate', interactive=False)
        print("[Django Server] Migrations up to date.", flush=True)
    except Exception as e:
        print(f"[Django Server] Warning: Migration check encountered: {e}", flush=True)

    # Launch server
    # Prefer gunicorn for production stability (handles Cloud Run concurrent health probes & keepalive)
    try:
        import gunicorn
        from gunicorn.app.base import BaseApplication

        class DjangoGunicornApp(BaseApplication):
            def __init__(self, options=None):
                self.options = options or {}
                super().__init__()

            def load_config(self):
                for key, value in self.options.items():
                    if key in self.cfg.settings and value is not None:
                        self.cfg.set(key.lower(), value)

            def load(self):
                from django.core.wsgi import get_wsgi_application
                return get_wsgi_application()

        options = {
            'bind': bind_address,
            'workers': 2,
            'threads': 4,
            'timeout': 120,
            'accesslog': '-',
            'errorlog': '-',
            'loglevel': 'info',
        }
        print(f"[Django Server] Starting Gunicorn WSGI server on {bind_address}...", flush=True)
        DjangoGunicornApp(options).run()
    except Exception as e:
        print(f"[Django Server] Gunicorn init notice: {e}. Falling back to Django runserver...", flush=True)
        from django.core.management import execute_from_command_line
        sys.argv = ['manage.py', 'runserver', bind_address, '--noreload']
        execute_from_command_line(sys.argv)

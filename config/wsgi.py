import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Ensure database tables are automatically migrated on WSGI boot
try:
    import django
    django.setup()
    from django.core.management import call_command
    call_command("migrate", interactive=False)
except Exception as e:
    print(f"WSGI Auto-Migrate Notice: {e}")

application = get_wsgi_application()

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Ensure database tables are automatically migrated and default admin user exists on boot
try:
    import django
    django.setup()
    from django.core.management import call_command
    call_command("migrate", interactive=False)

    from hospital.models import User
    if not User.objects.filter(is_superuser=True).exists():
        admin_user = User.objects.create_superuser(
            username="admin",
            email="admin@carepoint.com",
            password="adminpassword123",
            role=User.Role.ADMIN,
            is_staff=True,
            is_superuser=True,
        )
        print("WSGI Seed: Default admin user created successfully (username: admin, password: adminpassword123)")
except Exception as e:
    print(f"WSGI Auto-Migrate Notice: {e}")

application = get_wsgi_application()

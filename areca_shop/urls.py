from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from django.http import HttpResponse
from django.core.management import call_command
from django.contrib.auth import get_user_model

from store import views


# Temporary function to run migrations
def run_migrations(request):
    try:
        call_command('migrate')
        return HttpResponse("✅ Migrations applied successfully!")
    except Exception as e:
        return HttpResponse(f"❌ Error during migration: {e}")


# Temporary function to create a superuser
def create_admin(request):
    try:
        User = get_user_model()
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser("admin", "admin@example.com", "adminpassword123")
            return HttpResponse("✅ Superuser 'admin' created!")
        else:
            return HttpResponse("ℹ️ Superuser 'admin' already exists.")
    except Exception as e:
        return HttpResponse(f"❌ Error creating superuser: {e}")


urlpatterns = [
    path('', include('store.urls')),  # root handled by store app
    path('admin/', admin.site.urls),

    # ✅ Temporary endpoints (REMOVE after first use)
    path('run-migrations/', run_migrations),
    path('create-admin/', create_admin),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# bodega/urls.py

from django.contrib import admin
from django.urls import path, include
from inventario import views as inventario_views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views  # Asegúrate de importar esto

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', inventario_views.inicio, name='inicio'),
    path('inventario/', include('inventario.urls')),
    path('accounts/', include('django.contrib.auth.urls')),  # Incluye las URLs de autenticación de Django
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

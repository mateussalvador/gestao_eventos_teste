from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from rest_framework.authtoken.views import obtain_auth_token # [cite: 729]
from core.views import home_view

urlpatterns = [
    path('', home_view, name='home'),
    path('admin/', admin.site.urls),
    
    # Rotas da API
    path('api/', include('core.urls')),
    
    # Rota de Autenticação via Token (Conforme PDF 07)
    path('api/token/', obtain_auth_token, name='api_token_auth'), # 
    
    # Login via Session (opcional, mas útil para o navegador)
    path('api-auth/', include('rest_framework.urls')),

    # Docs
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
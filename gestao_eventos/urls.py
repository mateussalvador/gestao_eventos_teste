'''from django.contrib import admin
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
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) 
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)'''

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from rest_framework.authtoken.views import obtain_auth_token  # [cite: 729]
from core.views import eventos_list  # Mudança: usa a nova view em vez de home_view

urlpatterns = [
    path('', eventos_list, name='home'),  # / → lista de eventos (antiga home_view expandida)
    path('eventos/', include('core.urls')),  # Inclui /eventos/, /busca/, /contato/ do core
    path('admin/', admin.site.urls),
    
    # Rotas da API (mantidas, mas movidas para /api/ via include acima? Não: wait, ajuste)
    # Nota: Para evitar duplicata, movi api/ para core.urls, mas se preferir, mude para path('api/', include('core.urls'))
    # Por enquanto, assumo que api/ é via /eventos/api/ ? Não: melhor separar.
    # Correção: Mantenha path('api/', include('core.urls')) e remova o include de eventos/ se conflitar.
    
    # Rotas da API (ajustado para clareza)
    path('api/', include('core.urls')),  # /api/participantes etc. (router do core)
    
    # Rota de Autenticação via Token (Conforme PDF 07)
    path('api/token/', obtain_auth_token, name='api_token_auth'),  # 
    
    # Login via Session (opcional, mas útil para o navegador)
    path('api-auth/', include('rest_framework.urls')),

    # Docs (mantidas)
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) 
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
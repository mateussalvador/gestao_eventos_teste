'''from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ParticipanteViewSet, EventoViewSet, AtividadeViewSet, InscricaoViewSet

router = DefaultRouter()
router.register(r'participantes', ParticipanteViewSet)
router.register(r'eventos', EventoViewSet)
router.register(r'atividades', AtividadeViewSet)
router.register(r'inscricoes', InscricaoViewSet)

urlpatterns = [
    path('', include(router.urls)),
]'''

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ParticipanteViewSet, EventoViewSet, AtividadeViewSet, InscricaoViewSet,
    # Novas views HTML
    eventos_list, busca_eventos, contato
)

router = DefaultRouter()
router.register(r'participantes', ParticipanteViewSet)
router.register(r'eventos', EventoViewSet)
router.register(r'atividades', AtividadeViewSet)
router.register(r'inscricoes', InscricaoViewSet)

urlpatterns = [
    path('', include(router.urls)),  # Rotas API mantidas

    # Novas rotas Frontend (HTML, acessíveis via /api/ não, mas via raiz no urls.py principal)
    path('eventos/', eventos_list, name='eventos_list'),  # /eventos/ → lista com filtros
    path('busca/', busca_eventos, name='busca_eventos'),  # /busca/?q=termo
    path('contato/', contato, name='contato'),  # /contato/ com form
]
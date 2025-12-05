from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ParticipanteViewSet, EventoViewSet, AtividadeViewSet, InscricaoViewSet

router = DefaultRouter()
router.register(r'participantes', ParticipanteViewSet)
router.register(r'eventos', EventoViewSet)
router.register(r'atividades', AtividadeViewSet)
router.register(r'inscricoes', InscricaoViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
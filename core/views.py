from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count
from django.shortcuts import get_object_or_404, render
from django_filters.rest_framework import DjangoFilterBackend # [cite: 974]

from .models import Participante, Evento, Atividade, Inscricao
from .serializers import (
    ParticipanteSerializer, EventoSerializer, 
    AtividadeSerializer, InscricaoSerializer, EventoDashboardSerializer
)

def home_view(request):
    eventos = Evento.objects.all().order_by('data_inicio')
    return render(request, 'index.html', {'eventos': eventos})

class ParticipanteViewSet(viewsets.ModelViewSet):
    queryset = Participante.objects.all()
    serializer_class = ParticipanteSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    # Filtros e Busca
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['username', 'email', 'nome']
    filterset_fields = ['tipo']

class EventoViewSet(viewsets.ModelViewSet):
    """
    CRUD de Eventos com Filtros e Busca.
    """
    queryset = Evento.objects.all()
    serializer_class = EventoSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly] # 

    # Configuração de Filtros (PDF 06)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nome', 'descricao', 'local'] # Busca textual
    ordering_fields = ['data_inicio', 'nome']      # Ordenação
    filterset_fields = ['local']                   # Filtro exato

    @action(detail=True, methods=['get', 'post'], permission_classes=[permissions.IsAuthenticated])
    def participantes(self, request, pk=None):
        evento = self.get_object()
        if request.method == 'POST':
            inscricao, created = Inscricao.objects.get_or_create(participante=request.user, evento=evento)
            if created:
                return Response({'status': 'Inscrição realizada'}, status=status.HTTP_201_CREATED)
            return Response({'status': 'Já inscrito'}, status=status.HTTP_400_BAD_REQUEST)
        
        inscritos = Participante.objects.filter(eventos_inscritos=evento)
        serializer = ParticipanteSerializer(inscritos, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get', 'post'])
    def atividades(self, request, pk=None):
        evento = self.get_object()
        if request.method == 'POST':
            serializer = AtividadeSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(evento=evento)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        atividades = Atividade.objects.filter(evento=evento)
        serializer = AtividadeSerializer(atividades, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def dashboard(self, request, pk=None):
        evento = self.get_object()
        stats = Evento.objects.filter(pk=pk).annotate(
            total_inscritos=Count('participantes', distinct=True),
            total_atividades=Count('atividades', distinct=True)
        ).first()
        serializer = EventoDashboardSerializer(stats)
        return Response(serializer.data)

class AtividadeViewSet(viewsets.ModelViewSet):
    queryset = Atividade.objects.all()
    serializer_class = AtividadeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    # Filtros Avançados (PDF 06 + Enunciado)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['tipo', 'evento'] # Filtra por tipo (workshop, palestra) e evento
    search_fields = ['titulo']

    @action(detail=True, methods=['get', 'put', 'patch'])
    def responsavel(self, request, pk=None):
        atividade = self.get_object()
        if request.method in ['PUT', 'PATCH']:
            responsavel_id = request.data.get('responsavel_id')
            if not responsavel_id:
                return Response({'error': 'ID necessário'}, status=status.HTTP_400_BAD_REQUEST)
            responsavel = get_object_or_404(Participante, pk=responsavel_id)
            atividade.responsavel = responsavel
            atividade.save()
            return Response({'status': f'Responsável: {responsavel.username}'})
        
        if atividade.responsavel:
            serializer = ParticipanteSerializer(atividade.responsavel)
            return Response(serializer.data)
        return Response({'status': 'Sem responsável'}, status=status.HTTP_404_NOT_FOUND)

class InscricaoViewSet(viewsets.ModelViewSet):
    queryset = Inscricao.objects.all()
    serializer_class = InscricaoSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status']

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Inscricao.objects.all()
        return Inscricao.objects.filter(participante=user)

    def perform_create(self, serializer):
        serializer.save(participante=self.request.user)
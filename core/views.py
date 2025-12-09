from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authtoken.models import Token # importante para autenticação por token
from django.db.models import Count, Q, Case, When   # para agregações e filtros complexos
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse # para respostas HTTP personalizadas
from django_filters.rest_framework import DjangoFilterBackend # [cite: 974]
from django.views.decorators.cache import cache_page # para cache de views
from django.utils.decorators import method_decorator # para aplicar decoradores em métodos de classe
import csv # para exportação CSV

from .models import Participante, Evento, Atividade, Inscricao
from .serializers import (
    ParticipanteSerializer,ParticipanteRegistroSerializer, EventoSerializer, 
    AtividadeSerializer, InscricaoSerializer, EventoDashboardSerializer, RelatorioParticipacaoSerializer
)
from .permissions import IsOrganizadorOrReadOnly, IsResponsavelOrReadOnly # permissões customizadas

def home_view(request):
    eventos = Evento.objects.all().order_by('data_inicio')
    return render(request, 'index.html', {'eventos': eventos})

class ParticipanteViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciamento de participantes.

    Permite operações CRUD completas em participantes, com autenticação obrigatória.
    Inclui endpoint público de registro que cria usuário e retorna token automaticamente.

    Métodos suportados:
    - list: Lista todos os participantes (GET /api/v1/participantes/)
    - create: Cria novo participante (POST /api/v1/participantes/)
    - retrieve: Detalhes de um participante (GET /api/v1/participantes/{id}/)
    - update: Atualiza participante (PUT /api/v1/participantes/{id}/)
    - partial_update: Atualização parcial (PATCH /api/v1/participantes/{id}/)
    - destroy: Remove participante (DELETE /api/v1/participantes/{id}/)

    Códigos de resposta:
    - 200: Sucesso (list, retrieve)
    - 201: Criado (create, registro)
    - 400: Dados inválidos
    - 401: Não autenticado
    - 403: Permissão negada
    - 404: Não encontrado
    """
    queryset = Participante.objects.all()
    serializer_class = ParticipanteSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    # Filtros e Busca
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['username', 'email', 'celular', 'tipo', 'nome']
    filterset_fields = ['tipo']

@action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny]) # endpoint público
def registro(self, request):
        """
        Endpoint público para registro de novos participantes.

        Cria usuário com senha hashada automaticamente e retorna token de autenticação.

        Parâmetros esperados no body:
        - username: string (obrigatório)
        - email: string (obrigatório)
        - password: string (obrigatório)
        - password_confirm: string (obrigatório, deve coincidir com password)
        - celular: string (opcional)
        - tipo: string (opcional, padrão 'estudante')

        Retorno: {'token': str, 'user_id': int, 'username': str}
        """
        serializer = ParticipanteRegistroSerializer(data=request.data)
        if serializer.is_valid():
            participante = serializer.save()
            token, created = Token.objects.get_or_create(user=participante)
            return Response({
                'token': token.key,
                'user_id': participante.id,
                'username': participante.username
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(cache_page(60 * 15), name='list') 
class EventoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciamento de eventos.

    Apenas organizadores podem criar/editar eventos. Leitura é pública.
    Inclui ações customizadas para inscrição, atividades e relatórios.

    Métodos suportados:
    - list: Lista eventos com paginação (GET /api/v1/eventos/) - Cache de 15 minutos
    - create: Cria novo evento (POST /api/v1/eventos/) - Apenas organizadores
    - retrieve: Detalhes do evento (GET /api/v1/eventos/{id}/)
    - update: Atualiza evento (PUT /api/v1/eventos/{id}/) - Apenas organizadores
    - partial_update: Atualização parcial (PATCH /api/v1/eventos/{id}/)
    - destroy: Remove evento (DELETE /api/v1/eventos/{id}/)

    Ações customizadas:
    - participantes: Gerenciar inscrições (GET/POST /api/v1/eventos/{id}/participantes/)
    - atividades: Gerenciar atividades (GET/POST /api/v1/eventos/{id}/atividades/)
    - dashboard: Estatísticas do evento (GET /api/v1/eventos/{id}/dashboard/) - Cache de 15 minutos
    - relatorio_participacao: Relatório de participantes (GET /api/v1/eventos/{id}/relatorio_participacao/)

    Códigos de resposta: 200, 201, 400, 401, 403, 404
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
        """
        Gerencia inscrições no evento.

        GET: Lista participantes inscritos no evento.
        POST: Inscreve o usuário atual no evento (se não estiver inscrito).

        Parâmetros:
        - pk: ID do evento

        Retorno GET: Lista de participantes serializados
        Retorno POST: {'status': 'Inscrição realizada'} ou {'status': 'Já inscrito'}
        """
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
        """
        Gerencia atividades do evento.

        GET: Lista atividades do evento.
        POST: Cria nova atividade para o evento.

        Parâmetros:
        - pk: ID do evento
        - POST body: Dados da atividade (titulo, descricao, horario_inicio, horario_fim, tipo)

        Retorno GET: Lista de atividades serializadas
        Retorno POST: Atividade criada ou erros de validação
        """
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
    
    @method_decorator(cache_page(60 * 15)) # Cache por 15 minutos
    @action(detail=True, methods=['get'])
    def dashboard(self, request, pk=None):
        """
        Retorna estatísticas completas do evento (cache de 15 minutos).

        Inclui contadores, distribuições por tipo e listas de responsáveis/participantes.

        Parâmetros:
        - pk: ID do evento

        Retorno: Estatísticas do evento com agregações por tipo
        """
        evento = self.get_object()
        stats = Evento.objects.filter(pk=pk).annotate(
            total_inscritos=Count('participantes', distinct=True),
            total_atividades=Count('atividades', distinct=True)
        ).prefetch_related('atividades__responsavel', 'participantes').first() # otimiza consultas
        serializer = EventoDashboardSerializer(stats)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated]) # Apenas autenticados
    def relatorio_participacao(self, request, pk=None): 
        """
        Gera relatório detalhado de participação no evento.

        Lista todos os participantes inscritos com informações sobre atividades que ministram.
        Suporta exportação em CSV via parâmetro 'formato=csv'.

        Parâmetros:
        - pk: ID do evento
        - formato: 'csv' para exportar em CSV, padrão JSON

        Retorno: Lista de inscrições com dados dos participantes e atividades ministradas
        """
        evento = self.get_object()
        inscricoes = Inscricao.objects.filter(evento=evento).select_related('participante').prefetch_related('evento__atividades') # otimiza consultas

        formato = request.query_params.get('formato') # verifica formato solicitado
        if formato == 'csv':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="relatorio_participacao.csv"'
            writer = csv.writer(response)
            writer.writerow(['Participante', 'Email', 'Tipo', 'Atividades Ministradas'])
            for inscricao in inscricoes:
                atividades = ', '.join([a.titulo for a in inscricao.evento.atividades.filter(responsavel=inscricao.participante)])
                writer.writerow([
                    inscricao.participante.username,
                    inscricao.participante.email,
                    inscricao.participante.get_tipo_display(),
                    atividades
                ])
            return response
        else:
            serializer = RelatorioParticipacaoSerializer(inscricoes, many=True)
            return Response(serializer.data)

@method_decorator(cache_page(60 * 15), name='list')
class AtividadeViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciamento de atividades.

    Apenas responsáveis podem editar suas atividades. Leitura é pública.
    Inclui ação customizada para definir responsável.

    Métodos suportados:
    - list: Lista atividades com filtros (GET /api/v1/atividades/) - Cache de 15 minutos
    - create: Cria atividade (POST /api/v1/atividades/)
    - retrieve: Detalhes da atividade (GET /api/v1/atividades/{id}/)
    - update: Atualiza atividade (PUT /api/v1/atividades/{id}/) - Apenas responsável
    - partial_update: Atualização parcial (PATCH /api/v1/atividades/{id}/)
    - destroy: Remove atividade (DELETE /api/v1/atividades/{id}/)

    Ação customizada:
    - responsavel: Gerenciar responsável (GET/PUT/PATCH /api/v1/atividades/{id}/responsavel/)

    Códigos de resposta: 200, 201, 400, 401, 403, 404
    """
    queryset = Atividade.objects.all()
    serializer_class = AtividadeSerializer
    permission_classes = [IsResponsavelOrReadOnly] # Leitura pública, escrita autenticada

    # Filtros Avançados (PDF 06 + Enunciado)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['tipo', 'evento'] # Filtra por tipo (workshop, palestra) e evento
    search_fields = ['titulo']

    @action(detail=True, methods=['get', 'put', 'patch'])
    def responsavel(self, request, pk=None):
        """
        Gerencia o responsável pela atividade.

        GET: Retorna dados do responsável atual.
        PUT/PATCH: Define novo responsável (requer 'responsavel_id' no body).

        Parâmetros:
        - pk: ID da atividade
        - PUT/PATCH body: {'responsavel_id': int}

        Retorno GET: Dados do responsável ou {'status': 'Sem responsável'}
        Retorno PUT/PATCH: {'status': 'Responsável: {username}'}
        """
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
    """
    ViewSet para gerenciamento de inscrições.

    Usuários podem gerenciar suas próprias inscrições. Admins veem todas.

    Métodos suportados:
    - list: Lista inscrições do usuário (ou todas para admin) (GET /api/v1/inscricoes/)
    - create: Cria inscrição (POST /api/v1/inscricoes/) - Participante atual
    - retrieve: Detalhes da inscrição (GET /api/v1/inscricoes/{id}/)
    - update: Atualiza inscrição (PUT /api/v1/inscricoes/{id}/)
    - partial_update: Atualização parcial (PATCH /api/v1/inscricoes/{id}/)
    - destroy: Cancela inscrição (DELETE /api/v1/inscricoes/{id}/)

    Códigos de resposta: 200, 201, 400, 401, 403, 404
    """
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
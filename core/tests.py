from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from .models import Evento, Atividade, Inscricao

User = get_user_model()

class GestaoEventosTests(APITestCase):

    def setUp(self):
        """
        Configuração inicial rodada antes de CADA teste.
        Criamos usuários e tokens para simular os cenários.
        """
        # 1. Criar Usuário
        self.user = User.objects.create_user(
            username='testuser', 
            password='password123',
            email='test@example.com',
            tipo='estudante'
        )
        
        # 2. Configurar Cliente Autenticado (Token)
        self.client = APIClient()
        # Forçamos a autenticação para os testes que exigem login
        self.client.force_authenticate(user=self.user)
        
        # 3. Criar dados de exemplo
        self.evento_data = {
            "nome": "Python Conference",
            "descricao": "Maior evento de Python",
            "data_inicio": "2024-12-01T09:00:00Z",
            "data_fim": "2024-12-03T18:00:00Z",
            "local": "Centro de Convenções"
        }

    # --- TESTES DE AUTENTICAÇÃO E PERMISSÃO ---

    def test_criar_evento_sem_autenticacao(self):
        """Garante que usuários anônimos NÃO podem criar eventos (PDF 07)"""
        client_anonimo = APIClient() # Cliente sem token
        response = client_anonimo.post('/api/eventos/', self.evento_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_criar_evento_com_autenticacao(self):
        """Garante que usuário logado pode criar evento"""
        response = self.client.post('/api/eventos/', self.evento_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Evento.objects.count(), 1)
        self.assertEqual(Evento.objects.get().nome, "Python Conference")

    # --- TESTES DE RELACIONAMENTO E LÓGICA ---

    def test_inscricao_em_evento(self):
        """Testa a Action personalizada 'participantes' para se inscrever"""
        # Primeiro cria o evento
        evento = Evento.objects.create(**self.evento_data)
        
        # Tenta se inscrever na rota /api/eventos/{id}/participantes/
        url = f'/api/eventos/{evento.id}/participantes/'
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Verifica se gravou no banco
        self.assertTrue(Inscricao.objects.filter(participante=self.user, evento=evento).exists())

    def test_evitar_inscricao_duplicada(self):
        """Garante que não pode se inscrever duas vezes no mesmo evento"""
        evento = Evento.objects.create(**self.evento_data)
        url = f'/api/eventos/{evento.id}/participantes/'
        
        self.client.post(url) # Primeira vez (OK)
        response = self.client.post(url) # Segunda vez (Deve falhar/avisar)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # --- TESTES DE FILTROS (PDF 06) ---
    
    def test_filtro_busca_evento(self):
        """Testa se a busca por nome está funcionando"""
        Evento.objects.create(nome="Evento Python", descricao="X", data_inicio="2024-01-01T00:00:00Z", data_fim="2024-01-01T00:00:00Z", local="A")
        Evento.objects.create(nome="Evento Java", descricao="Y", data_inicio="2024-01-01T00:00:00Z", data_fim="2024-01-01T00:00:00Z", local="B")
        
        # Busca por 'Python'
        response = self.client.get('/api/eventos/?search=Python')
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['nome'], "Evento Python")

    def test_dashboard_dados(self):
        """Testa se o dashboard retorna os contadores corretos"""
        evento = Evento.objects.create(**self.evento_data)
        Inscricao.objects.create(participante=self.user, evento=evento)
        
        url = f'/api/eventos/{evento.id}/dashboard/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_inscritos'], 1)
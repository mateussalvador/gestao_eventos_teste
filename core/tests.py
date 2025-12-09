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

    def test_relatorio_participacao_json(self):
        """Testa se o relatório de participação retorna JSON corretamente"""
        evento = Evento.objects.create(**self.evento_data)
        Inscricao.objects.create(participante=self.user, evento=evento)

        url = f'/api/v1/eventos/{evento.id}/relatorio_participacao/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['participante_nome'], self.user.username)

    def test_relatorio_participacao_csv(self):
        """Testa se o relatório de participação retorna CSV corretamente"""
        evento = Evento.objects.create(**self.evento_data)
        Inscricao.objects.create(participante=self.user, evento=evento)

        url = f'/api/v1/eventos/{evento.id}/relatorio_participacao/?formato=csv'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn('attachment; filename="relatorio_participacao.csv"', response['Content-Disposition'])
        # Check if CSV content contains the username
        content = response.content.decode('utf-8')
        self.assertIn(self.user.username, content)

class TestEventoModel(APITestCase):

    def test_evento_data_fim_antes_inicio_invalida(self):
        """Testa validação de datas: data_fim deve ser posterior a data_inicio"""
        from django.core.exceptions import ValidationError
        evento = Evento(
            nome="Evento Teste",
            descricao="Descrição",
            data_inicio="2024-12-02T10:00:00Z",
            data_fim="2024-12-01T10:00:00Z",  # Antes do início
            local="Local"
        )
        with self.assertRaises(ValidationError):
            evento.full_clean()

    def test_evento_str_representation(self):
        """Testa método __str__ do modelo Evento"""
        evento = Evento.objects.create(
            nome="Evento Teste",
            descricao="Descrição",
            data_inicio="2026-12-01T10:00:00Z",
            data_fim="2026-12-02T10:00:00Z",
            local="Local"
        )
        self.assertEqual(str(evento), "Evento Teste")

class TestAtividadeModel(APITestCase):

    def setUp(self):
        self.evento = Evento.objects.create(
            nome="Evento Teste",
            descricao="Descrição",
            data_inicio="2026-12-01T09:00:00Z",
            data_fim="2026-12-03T18:00:00Z",
            local="Local"
        )

    def test_atividade_horario_invalido(self):
        """Testa validação de horários: horario_fim deve ser posterior a horario_inicio"""
        from django.core.exceptions import ValidationError
        atividade = Atividade(
            evento=self.evento,
            titulo="Atividade Teste",
            horario_inicio="2024-12-01T15:00:00Z",
            horario_fim="2024-12-01T14:00:00Z",  # Antes do início
            tipo="palestra"
        )
        with self.assertRaises(ValidationError):
            atividade.full_clean()

    def test_atividade_fora_periodo_evento(self):
        """Testa validação: atividade deve estar dentro do período do evento"""
        from django.core.exceptions import ValidationError
        atividade = Atividade(
            evento=self.evento,
            titulo="Atividade Teste",
            horario_inicio="2024-12-04T10:00:00Z",  # Depois do fim do evento
            horario_fim="2024-12-04T12:00:00Z",
            tipo="palestra"
        )
        with self.assertRaises(ValidationError):
            atividade.full_clean()

    def test_conflito_horario_responsavel(self):
        """Testa validação de conflito de horário do responsável"""
        from django.core.exceptions import ValidationError
        responsavel = User.objects.create_user(
            username='responsavel',
            password='pass',
            tipo='palestrante'
        )
        # Criar primeira atividade
        Atividade.objects.create(
            evento=self.evento,
            responsavel=responsavel,
            titulo="Atividade 1",
            horario_inicio="2026-12-01T10:00:00Z",
            horario_fim="2026-12-01T12:00:00Z",
            tipo="palestra"
        )
        # Tentar criar segunda atividade no mesmo horário
        atividade_conflito = Atividade(
            evento=self.evento,
            responsavel=responsavel,
            titulo="Atividade 2",
            horario_inicio="2026-12-01T11:00:00Z",  # Sobreposto
            horario_fim="2026-12-01T13:00:00Z",
            tipo="palestra"
        )
        with self.assertRaises(ValidationError):
            atividade_conflito.full_clean()

class TestInscricaoModel(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='pass',
            tipo='estudante'
        )

    def test_inscricao_antes_evento(self):
        """Testa validação: pode se inscrever antes do evento começar"""
        evento = Evento.objects.create(
            nome="Evento Futuro",
            descricao="Descrição",
            data_inicio="2026-12-01T10:00:00Z",  # Data no futuro
            data_fim="2026-12-02T10:00:00Z",
            local="Local"
        )
        inscricao = Inscricao(
            participante=self.user,
            evento=evento
        )
        # Deve passar sem erro
        inscricao.full_clean()

    def test_inscricao_durante_evento(self):
        """Testa validação: pode se inscrever durante o evento"""
        evento = Evento.objects.create(
            nome="Evento Atual",
            descricao="Descrição",
            data_inicio="2024-12-01T10:00:00Z",  # Data no passado
            data_fim="2026-12-02T10:00:00Z",  # Data no futuro
            local="Local"
        )
        inscricao = Inscricao(
            participante=self.user,
            evento=evento
        )
        # Deve passar sem erro
        inscricao.full_clean()

    def test_inscricao_depois_evento(self):
        """Testa validação: não pode se inscrever após o evento terminar"""
        evento = Evento.objects.create(
            nome="Evento Passado",
            descricao="Descrição",
            data_inicio="2023-01-01T10:00:00Z",
            data_fim="2023-01-02T10:00:00Z",  # Data no passado
            local="Local"
        )
        from django.core.exceptions import ValidationError
        inscricao = Inscricao(
            participante=self.user,
            evento=evento
        )
        with self.assertRaises(ValidationError):
            inscricao.full_clean()
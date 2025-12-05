from django.db import models
from django.contrib.auth.models import AbstractUser

# 1. Entidade Participante (Herança do User do Django) [cite: 51]
class Participante(AbstractUser):
    TIPO_CHOICES = (
        ('estudante', 'Estudante'),
        ('convidado', 'Convidado'),
        ('palestrante', 'Palestrante'),
        ('organizador', 'Organizador'),
    )
    # Campos adicionais solicitados no PDF [cite: 56]
    celular = models.CharField(max_length=20, blank=True, null=True)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='estudante')

    def __str__(self):
        return f"{self.username} ({self.get_tipo_display()})"

# 2. Entidade Evento [cite: 40]
class Evento(models.Model):
    nome = models.CharField(max_length=200)
    descricao = models.TextField()
    banner = models.ImageField(upload_to='banners/', blank=True, null=True) # Banner solicitado
    data_inicio = models.DateTimeField()
    data_fim = models.DateTimeField()
    local = models.CharField(max_length=255)
    
    # Relacionamento N:N explícito via tabela Inscricao [cite: 59]
    participantes = models.ManyToManyField(
        Participante, 
        through='Inscricao', 
        related_name='eventos_inscritos'
    )

    def __str__(self):
        return self.nome

# 3. Entidade Atividade [cite: 61]
class Atividade(models.Model):
    TIPO_ATIVIDADE = (
        ('palestra', 'Palestra'),
        ('workshop', 'Workshop'),
        ('oficina', 'Oficina'),
    )
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE, related_name='atividades') # [cite: 72]
    # Responsável pela atividade (ex: Palestrante) [cite: 73]
    responsavel = models.ForeignKey(
        Participante, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='atividades_ministradas'
    )
    titulo = models.CharField(max_length=200)
    descricao = models.TextField(blank=True)
    horario_inicio = models.DateTimeField()
    horario_fim = models.DateTimeField()
    tipo = models.CharField(max_length=20, choices=TIPO_ATIVIDADE)

    def __str__(self):
        return f"{self.titulo} - {self.evento.nome}"

# 4. Entidade Inscrição (Tabela Intermediária N:N) [cite: 28]
class Inscricao(models.Model):
    STATUS_CHOICES = (
        ('pendente', 'Pendente'),
        ('confirmado', 'Confirmado'),
        ('cancelado', 'Cancelado'),
    )
    participante = models.ForeignKey(Participante, on_delete=models.CASCADE)
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE)
    data_inscricao = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')

    class Meta:
        unique_together = ('participante', 'evento') # Evita inscrição duplicada
        verbose_name = 'Inscrição'
        verbose_name_plural = 'Inscrições'

    def __str__(self):
        return f"{self.participante.username} em {self.evento.nome}"
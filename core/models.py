from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError # import necessário para validações personalizadas
from django.utils import timezone # import necessário para manipulação de datas
from django.db.models import Q # import necessário para consultas complexas
from safedelete.models import SafeDeleteModel, SOFT_DELETE_CASCADE # import para soft delete

class TimeStampedModel(models.Model): # Modelo abstrato para timestamps
    created_at = models.DateTimeField(auto_now_add=True) # Data de criação
    updated_at = models.DateTimeField(auto_now=True) # Data de atualização

    class Meta: # Modelo abstrato para não criar tabela no banco de dados
        abstract = True
        
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

    def clean(self): # Validação personalizada para datas
        if self.data_fim <= self.data_inicio:
            raise ValidationError('A data de fim deve ser posterior à data de início.')

    def save(self, *args, **kwargs): # Sobrescreve o save para garantir validação
        self.full_clean() # Chama a validação personalizada
        super().save(*args, **kwargs) # Salva o objeto

    _safedelete_policy = SOFT_DELETE_CASCADE # Habilita soft delete com cascata
    
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

    def clean(self): # Validação personalizada para horários
        if self.horario_fim <= self.horario_inicio: # Verificar se o horário de fim é após o início
            raise ValidationError('O horário de fim deve ser posterior ao horário de início.')
        if self.horario_inicio < self.evento.data_inicio or self.horario_fim > self.evento.data_fim:
            raise ValidationError('A atividade deve estar dentro do período do evento.')
        # Verificar conflitos de horário do responsável
        if self.responsavel:
            conflitos = Atividade.objects.filter(
                responsavel=self.responsavel,
                evento=self.evento
            ).exclude(pk=self.pk).filter(
                Q(horario_inicio__lt=self.horario_fim) & Q(horario_fim__gt=self.horario_inicio)
            )
            if conflitos.exists():
                raise ValidationError('O responsável já tem uma atividade neste horário.')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

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

    def clean(self): # Validação personalizada para inscrição
        if self.evento.data_fim < timezone.now(): # Verifica se o evento já passou
            raise ValidationError('Não é possível se inscrever em eventos que já passaram.')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        unique_together = ('participante', 'evento') # Evita inscrição duplicada
        verbose_name = 'Inscrição'
        verbose_name_plural = 'Inscrições'

    def __str__(self):
        return f"{self.participante.username} em {self.evento.nome}"
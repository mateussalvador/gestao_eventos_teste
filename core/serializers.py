from rest_framework import serializers
from django.db.models import Count # import para agregações
from .models import Participante, Evento, Atividade, Inscricao

class ParticipanteRegistroSerializer(serializers.ModelSerializer): # Serializer para registro de participantes
    password_confirm = serializers.CharField(write_only=True)

    class Meta: # Meta do serializer
        model = Participante
        fields = ['username', 'email', 'password', 'password_confirm', 'celular', 'tipo']
        extra_kwargs = { 
            'password': {'write_only': True} # senha não será exibida
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("As senhas não coincidem.")
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = Participante.objects.create_user(**validated_data)
        return user

class ParticipanteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Participante
        fields = ['id', 'username', 'email', 'celular', 'tipo']

class AtividadeSerializer(serializers.ModelSerializer):
    responsavel_nome = serializers.CharField(source='responsavel.username', read_only=True)

    class Meta:
        model = Atividade
        fields = '__all__'

class InscricaoSerializer(serializers.ModelSerializer):
    participante_nome = serializers.CharField(source='participante.username', read_only=True)
    evento_nome = serializers.CharField(source='evento.nome', read_only=True)
    
    class Meta:
        model = Inscricao
        fields = ['id', 'evento', 'evento_nome', 'participante', 'participante_nome', 'data_inscricao', 'status']
        read_only_fields = ['data_inscricao']

class RelatorioParticipacaoSerializer(serializers.ModelSerializer): # Serializer para relatório de participação
    participante_nome = serializers.CharField(source='participante.username', read_only=True) # Nome do participante
    participante_email = serializers.CharField(source='participante.email', read_only=True) # Email do participante
    participante_tipo = serializers.CharField(source='participante.tipo', read_only=True)   # Tipo do participante
    atividades_responsavel = serializers.SerializerMethodField() # Atividades em que o participante é responsável

    class Meta: # Meta do serializer
        model = Inscricao
        fields = ['participante_nome', 'participante_email', 'participante_tipo', 'data_inscricao', 'status', 'atividades_responsavel']

    def get_atividades_responsavel(self, obj): # Método para obter atividades em que o participante é responsável
        atividades = Atividade.objects.filter(evento=obj.evento, responsavel=obj.participante)
        return [atividade.titulo for atividade in atividades]

class EventoSerializer(serializers.ModelSerializer):
    # Serializer aninhado para leitura (mostra as atividades dentro do evento)
    atividades = AtividadeSerializer(many=True, read_only=True)
    
    class Meta:
        model = Evento
        fields = ['id', 'nome', 'descricao', 'banner', 'data_inicio', 'data_fim', 'local', 'atividades']

# Serializer especial para o Dashboard [cite: 84]
class EventoDashboardSerializer(serializers.ModelSerializer):
    total_inscritos = serializers.IntegerField(read_only=True)
    total_atividades = serializers.IntegerField(read_only=True)
    participantes_por_tipo = serializers.SerializerMethodField() # Novo campo para participantes por tipo
    atividades_por_tipo = serializers.SerializerMethodField() # Novo campo para atividades por tipo
    responsaveis_atividades = serializers.SerializerMethodField() # Novo campo para responsáveis por atividades
    participantes_sem_atividade = serializers.SerializerMethodField() # Novo campo para participantes sem atividade
    atividades = AtividadeSerializer(many=True, read_only=True) 

    class Meta:
        model = Evento
        fields = ['id', 'nome', 'local', 'total_inscritos', 'total_atividades', 'participantes_por_tipo', 'atividades_por_tipo', 'responsaveis_atividades', 'participantes_sem_atividade', 'atividades']

    def get_participantes_por_tipo(self, obj): # Método para obter contagem de participantes por tipo
        tipos = Inscricao.objects.filter(evento=obj).values('participante__tipo').annotate(count=Count('participante__tipo')).order_by('participante__tipo')
        return {tipo['participante__tipo']: tipo['count'] for tipo in tipos}
 
    def get_atividades_por_tipo(self, obj): # Método para obter contagem de atividades por tipo
        tipos = obj.atividades.values('tipo').annotate(count=Count('tipo')).order_by('tipo')
        return {tipo['tipo']: tipo['count'] for tipo in tipos}

    def get_responsaveis_atividades(self, obj): # Método para obter lista de responsáveis por atividades
        responsaveis = obj.atividades.exclude(responsavel__isnull=True).values_list('responsavel__username', flat=True).distinct()
        return list(responsaveis)

    def get_participantes_sem_atividade(self, obj): # Método para obter participantes sem atividade atribuída
        participantes_com_atividade = obj.atividades.exclude(responsavel__isnull=True).values_list('responsavel', flat=True)
        sem_atividade = Inscricao.objects.filter(evento=obj).exclude(participante__in=participantes_com_atividade).values_list('participante__username', flat=True)
        return list(sem_atividade)
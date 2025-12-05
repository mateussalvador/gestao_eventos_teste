from rest_framework import serializers
from .models import Participante, Evento, Atividade, Inscricao

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
    atividades = AtividadeSerializer(many=True, read_only=True)

    class Meta:
        model = Evento
        fields = ['id', 'nome', 'local', 'total_inscritos', 'total_atividades', 'atividades']
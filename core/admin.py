from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Participante, Evento, Atividade, Inscricao

@admin.register(Participante)
class ParticipanteAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Informações Adicionais', {'fields': ('celular', 'tipo')}),
    )
    list_display = ('username', 'email', 'tipo', 'celular')
    list_filter = ('tipo', 'is_staff')

class AtividadeInline(admin.TabularInline):
    model = Atividade
    extra = 1

@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'data_inicio', 'local')
    search_fields = ('nome',)
    inlines = [AtividadeInline] # Permite criar atividades dentro da tela de Evento

@admin.register(Atividade)
class AtividadeAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'evento', 'horario_inicio', 'tipo', 'responsavel')
    list_filter = ('evento', 'tipo')

@admin.register(Inscricao)
class InscricaoAdmin(admin.ModelAdmin):
    list_display = ('participante', 'evento', 'data_inscricao', 'status')
    list_filter = ('status', 'evento')
    actions = ['confirmar_inscricao']

    def confirmar_inscricao(self, request, queryset):
        queryset.update(status='confirmado')
    confirmar_inscricao.short_description = "Confirmar inscrições selecionadas"
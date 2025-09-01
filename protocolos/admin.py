from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.db.models import Case, When
from django.utils.html import format_html
from .models import Cliente, Protocolo, Atualizacao, TipoProblema

# Customização do Admin de Usuários
class CustomUserAdmin(BaseUserAdmin):
    list_display = (
        'username', 'email', 'first_name', 'last_name', 'is_superuser'
    )
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (
            ('Permissions'),
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                    'groups',
                    'user_permissions',
                ),
            },
        ),
        (('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


# Admin para Tipos de Problemas
@admin.register(TipoProblema)
class TipoProblemaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'ativo', 'data_criacao', 'criado_por')
    list_filter = ('ativo', 'data_criacao')
    search_fields = ('nome', 'descricao')
    readonly_fields = ('data_criacao', 'criado_por')
    
    fieldsets = (
        ('Informações do Tipo de Problema', {
            'fields': ('nome', 'descricao', 'ativo')
        }),
        ('Controle', {
            'fields': ('data_criacao', 'criado_por'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if not obj.pk:  # Se for um novo tipo de problema
            obj.criado_por = request.user
        super().save_model(request, obj, form, change)

    def has_add_permission(self, request):
        # Apenas superusuários podem adicionar tipos de problemas
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        # Apenas superusuários podem excluir tipos de problemas
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        # Apenas superusuários podem modificar tipos de problemas
        return request.user.is_superuser


# Inline para Atualizações no Admin de Protocolos
class AtualizacaoInline(admin.TabularInline):
    model = Atualizacao
    extra = 1  # Permite adicionar uma atualização diretamente
    fields = ('descricao', 'usuario', 'data_hora')
    readonly_fields = ('usuario', 'data_hora')

    def save_model(self, request, obj, form, change):
        if not obj.pk:  # Se for uma nova atualização
            obj.usuario = request.user
        super().save_model(request, obj, form, change)


# Customização do Admin de Protocolos
@admin.register(Protocolo)
class ProtocoloAdmin(admin.ModelAdmin):
    def cliente_principal(self, obj):
        """Método que pega o nome do primeiro cliente atrelado ao protocolo."""
        cliente = obj.clientes.first()
        if cliente:
            return cliente.nome
        return "N/A" # "N/A" significa Não Aplicável

    cliente_principal.short_description = "Cliente Principal"

    def numero_com_tooltip(self, obj):
        """Exibe o número do protocolo com a última atualização em um tooltip."""
        ultima_atualizacao = obj.atualizacoes.order_by('-data_hora').first()
        if ultima_atualizacao:
            tooltip_text = ultima_atualizacao.descricao
        else:
            tooltip_text = "Nenhuma atualização ainda."
        return format_html('<span title="{}">#{}</span>', tooltip_text, obj.numero)
    numero_com_tooltip.short_description = "Número"

    list_display = (
        'numero_com_tooltip', 'status', 'buic_dispositivo', 'cliente_principal', 'tipo_problema', 'usuario_criador', 'data_criacao', 'data_finalizacao'
    )
    list_filter = ('status', 'tipo_problema', 'data_criacao', 'usuario_criador')
    search_fields = ('numero__iexact', 'clientes__nome__icontains', 'descricao_problema__icontains', 'tipo_problema__nome__icontains')
    inlines = [AtualizacaoInline]
    
    # Campos organizados em fieldsets
    fieldsets = (
        ('Informações do Protocolo', {
            'fields': ('numero_exibicao', 'clientes', 'buic_dispositivo', 'tipo_problema', 'descricao_problema')
        }),
        ('Status e Controle', {
            'fields': ('status', 'usuario_criador', 'data_criacao', 'data_finalizacao')
        }),
    )
    
    # Campos somente leitura
    readonly_fields = ('numero_exibicao', 'usuario_criador', 'data_criacao', 'data_finalizacao')
    
    # Campos que aparecem ao criar um novo protocolo
    add_fieldsets = (
        ('Novo Protocolo', {
            'fields': ('numero_exibicao', 'clientes', 'buic_dispositivo', 'tipo_problema', 'descricao_problema')
        }),
    )

    def get_fieldsets(self, request, obj=None):
        if not obj:  # Criando um novo protocolo
            return self.add_fieldsets
        return super().get_fieldsets(request, obj)

    def get_readonly_fields(self, request, obj=None):
        readonly = list(self.readonly_fields)
        if not obj:  # Criando um novo protocolo
            return ['numero_exibicao']
        return readonly

    def numero_exibicao(self, obj):
        if obj and obj.numero:
            return f"#{obj.numero}"
        else:
            # Para novos protocolos, mostra qual número será gerado
            return f"#{Protocolo.get_proximo_numero()} (será gerado automaticamente)"
    numero_exibicao.short_description = "Número do Protocolo"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.order_by(
            Case(
                When(status='aberto', then=0),
                When(status='em_andamento', then=1),
                When(status='finalizado', then=2),
                default=99,
            )
        )

    def save_model(self, request, obj, form, change):
        if not obj.pk:  # Se for um novo protocolo
            obj.usuario_criador = request.user
        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            if not instance.pk:  # Se for uma nova atualização
                instance.usuario = request.user
            instance.save()
        formset.save_m2m()

# Customização do Admin de Clientes
@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nome', 'email', 'data_cadastro', 'ativo')
    search_fields = ('nome__icontains', 'email__icontains')
    list_filter = ('ativo', 'data_cadastro')


# Customização da interface administrativa
admin.site.site_header = "Sistema de Gestão de Protocolos"
admin.site.site_title = "Sistema de Protocolos"
admin.site.index_title = "Bem-vindo ao Admin do Sistema de Protocolos"
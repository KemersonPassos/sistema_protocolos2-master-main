from django import forms
from .models import Protocolo, Cliente, TipoProblema

class ProtocoloForm(forms.ModelForm):
    clientes = forms.ModelMultipleChoiceField(
        queryset=Cliente.objects.filter(ativo=True).order_by('nome'),
        widget=forms.SelectMultiple(attrs={
            'class': 'form-control select2-clientes',
            'data-placeholder': 'Digite o nome do cliente para buscar...',
            'data-allow-clear': 'true',
            'multiple': 'multiple'
        }),
        required=True,
        label="Clientes",
        help_text="Digite o nome do cliente para buscar. Você pode selecionar múltiplos clientes."
    )

    tipo_problema = forms.ModelChoiceField(
        queryset=TipoProblema.objects.filter(ativo=True).order_by('nome'),
        widget=forms.Select(attrs={
            'class': 'form-control',
            'data-placeholder': 'Selecione o tipo de problema...'
        }),
        required=True,
        label="Tipo de Problema",
        help_text="Selecione o tipo de problema que melhor descreve a situação."
    )

    class Meta:
        model = Protocolo
        fields = ["clientes", "buic_dispositivo", "tipo_problema", "descricao_problema"]
        widgets = {
            "buic_dispositivo": forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: BUIC-001'
            }),
            "descricao_problema": forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Descreva detalhadamente o problema...'
            }),
        }

class TipoProblemaForm(forms.ModelForm):
    """Form para superusuários adicionarem novos tipos de problemas"""
    
    class Meta:
        model = TipoProblema
        fields = ['nome', 'descricao']
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Problema de conectividade'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descrição detalhada do tipo de problema (opcional)'
            }),
        }
        labels = {
            'nome': 'Nome do Tipo de Problema',
            'descricao': 'Descrição (Opcional)'
        }

class AtualizacaoForm(forms.ModelForm):
    class Meta:
        model = Protocolo
        fields = ["descricao_problema"]
        widgets = {
            "descricao_problema": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Adicione a primeira atualização aqui (opcional)"
            }),
        }
        labels = {
            "descricao_problema": "Primeira Atualização (Opcional)"
        }
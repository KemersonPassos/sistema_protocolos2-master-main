from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class TipoProblema(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(blank=True, null=True)
    ativo = models.BooleanField(default=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    criado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Tipo de Problema"
        verbose_name_plural = "Tipos de Problemas"
        ordering = ['nome']

class Cliente(models.Model):
    nome = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    senha = models.CharField(max_length=255)  # Considerar usar um hash de senha mais seguro em produção
    data_cadastro = models.DateTimeField(auto_now_add=True)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"


class Protocolo(models.Model):
    STATUS_CHOICES = [
        ('aberto', 'Aberto'),
        ('em_andamento', 'Em Andamento'),
        ('finalizado', 'Finalizado'),
    ]

    numero = models.IntegerField(unique=True, blank=True, null=True)
    clientes = models.ManyToManyField(Cliente, related_name='protocolos')
    buic_dispositivo = models.CharField(max_length=255)
    tipo_problema = models.ForeignKey(TipoProblema, on_delete=models.PROTECT, related_name='protocolos')
    descricao_problema = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='aberto')
    usuario_criador = models.ForeignKey(User, on_delete=models.CASCADE, related_name='protocolos_criados')
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_finalizacao = models.DateTimeField(null=True, blank=True)

    @classmethod
    def get_proximo_numero(cls):
        """Retorna o próximo número de protocolo disponível"""
        ultimo_protocolo = cls.objects.order_by('-numero').first()
        if ultimo_protocolo and ultimo_protocolo.numero:
            return ultimo_protocolo.numero + 1
        else:
            return 1000

    def save(self, *args, **kwargs):
        if not self.numero:
            # Gerar próximo número automaticamente
            self.numero = self.get_proximo_numero()
        
        # Se o status foi alterado para finalizado, definir data_finalizacao
        if self.status == 'finalizado' and not self.data_finalizacao:
            self.data_finalizacao = timezone.now()
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Protocolo #{self.numero}"

    class Meta:
        verbose_name = "Protocolo"
        verbose_name_plural = "Protocolos"
        ordering = ['-data_criacao']


class Atualizacao(models.Model):
    protocolo = models.ForeignKey(Protocolo, on_delete=models.CASCADE, related_name='atualizacoes')
    descricao = models.TextField()
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    data_hora = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Atualizar status do protocolo para "em_andamento" se for a primeira atualização
        if self.protocolo.status == 'aberto':
            self.protocolo.status = 'em_andamento'
            self.protocolo.save()

    def __str__(self):
        return f"Atualização - {self.protocolo} - {self.data_hora.strftime('%d/%m/%Y %H:%M')}"

    class Meta:
        verbose_name = "Atualização"
        verbose_name_plural = "Atualizações"
        ordering = ['-data_hora']
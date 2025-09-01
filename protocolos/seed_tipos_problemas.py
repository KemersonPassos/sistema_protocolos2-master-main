from django.core.management.base import BaseCommand
from protocolos.models import TipoProblema

class Command(BaseCommand):
    help = 'Popula a tabela TipoProblema com os tipos de problemas padrão'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Criando tipos de problemas padrão...'))

        tipos_problemas_padrao = [
            {
                'nome': 'Equipamento queimado',
                'descricao': 'Equipamento apresenta falha por queima de componentes'
            },
            {
                'nome': 'Relé colado',
                'descricao': 'Problema relacionado ao travamento do relé'
            },
            {
                'nome': 'Erro de firmware',
                'descricao': 'Falha no software/firmware do equipamento'
            },
            {
                'nome': 'Falha de comunicação entre socket e interruptor',
                'descricao': 'Problema de comunicação entre os componentes'
            },
            {
                'nome': 'Perda de produto',
                'descricao': 'Problema que resulta em perda de produto'
            },
        ]

        for tipo_data in tipos_problemas_padrao:
            tipo_problema, created = TipoProblema.objects.get_or_create(
                nome=tipo_data['nome'],
                defaults={
                    'descricao': tipo_data['descricao'],
                    'ativo': True
                }
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Tipo de problema "{tipo_problema.nome}" criado.')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Tipo de problema "{tipo_problema.nome}" já existe.')
                )

        self.stdout.write(self.style.SUCCESS('Tipos de problemas padrão criados com sucesso!'))
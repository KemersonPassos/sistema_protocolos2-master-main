from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.admin.views.decorators import staff_member_required
from .models import Protocolo, Cliente, Atualizacao, TipoProblema
from .forms import ProtocoloForm, TipoProblemaForm
import csv
from django.http import HttpResponse
import json

@login_required
def dashboard(request):
    total_protocolos = Protocolo.objects.count()
    protocolos_abertos = Protocolo.objects.filter(status="aberto").count()
    protocolos_em_andamento = Protocolo.objects.filter(status="em_andamento").count()
    protocolos_finalizados = Protocolo.objects.filter(status="finalizado").count()

    ultimos_protocolos = Protocolo.objects.order_by("-data_criacao")[:5]

    # Estatísticas por tipo de problema (para o dashboard)
    problemas_stats = TipoProblema.objects.annotate(
        total_protocolos=Count('protocolos')
    ).filter(ativo=True, total_protocolos__gt=0).order_by('-total_protocolos')[:5]

    context = {
        "total_protocolos": total_protocolos,
        "protocolos_abertos": protocolos_abertos,
        "protocolos_em_andamento": protocolos_em_andamento,
        "protocolos_finalizados": protocolos_finalizados,
        "ultimos_protocolos": ultimos_protocolos,
        "problemas_stats": problemas_stats,
    }
    return render(request, "protocolos/dashboard.html", context)

@login_required
def novo_protocolo(request):
    if request.method == "POST":
        form = ProtocoloForm(request.POST)
        if form.is_valid():
            protocolo = form.save(commit=False)
            protocolo.usuario_criador = request.user
            protocolo.save()
            form.save_m2m()  # Salva o relacionamento ManyToMany para clientes

            # Adiciona a primeira atualização se houver
            descricao_primeira_atualizacao = request.POST.get("primeira_atualizacao")
            if descricao_primeira_atualizacao:
                Atualizacao.objects.create(
                    protocolo=protocolo,
                    descricao=descricao_primeira_atualizacao,
                    usuario=request.user
                )
            return redirect("dashboard")
    else:
        form = ProtocoloForm()
    
    # Verificar se o usuário é superusuário para mostrar opção de adicionar tipo de problema
    pode_adicionar_tipo = request.user.is_superuser
    
    context = {
        "form": form,
        "proximo_numero": Protocolo.get_proximo_numero(),
        "pode_adicionar_tipo": pode_adicionar_tipo,
        "form_tipo_problema": TipoProblemaForm() if pode_adicionar_tipo else None
    }
    
    return render(request, "protocolos/novo_protocolo.html", context)

@login_required
@require_POST
def adicionar_cliente(request):
    """Endpoint AJAX para adicionar novo cliente"""
    try:
        nome = request.POST.get('nome', '').strip()
        email = request.POST.get('email', '').strip()
        senha = request.POST.get('senha', '').strip()
        
        if not all([nome, email, senha]):
            return JsonResponse({
                'success': False,
                'error': 'Todos os campos são obrigatórios'
            })
        
        # Verificar se o email já existe
        if Cliente.objects.filter(email=email).exists():
            return JsonResponse({
                'success': False,
                'error': 'Já existe um cliente com este email'
            })
        
        # Criar o cliente
        cliente = Cliente.objects.create(
            nome=nome,
            email=email,
            senha=senha  # Em produção, usar hash da senha
        )
        
        return JsonResponse({
            'success': True,
            'cliente': {
                'id': cliente.id,
                'nome': cliente.nome,
                'email': cliente.email
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        })

@login_required
@require_POST
def adicionar_tipo_problema(request):
    """Endpoint AJAX para superusuários adicionarem novos tipos de problemas"""
    if not request.user.is_superuser:
        return JsonResponse({
            'success': False,
            'error': 'Apenas superusuários podem adicionar tipos de problemas'
        })
    
    try:
        nome = request.POST.get('nome', '').strip()
        descricao = request.POST.get('descricao', '').strip()
        
        if not nome:
            return JsonResponse({
                'success': False,
                'error': 'O nome do tipo de problema é obrigatório'
            })
        
        # Verificar se o nome já existe
        if TipoProblema.objects.filter(nome=nome).exists():
            return JsonResponse({
                'success': False,
                'error': 'Já existe um tipo de problema com este nome'
            })
        
        # Criar o tipo de problema
        tipo_problema = TipoProblema.objects.create(
            nome=nome,
            descricao=descricao,
            criado_por=request.user
        )
        
        return JsonResponse({
            'success': True,
            'tipo_problema': {
                'id': tipo_problema.id,
                'nome': tipo_problema.nome,
                'descricao': tipo_problema.descricao
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        })

@login_required
def busca_global(request):
    query = request.GET.get("q")
    resultados = []
    if query:
        # Busca em Protocolos
        protocolos_resultados = Protocolo.objects.filter(
            Q(numero__icontains=query) |
            Q(buic_dispositivo__icontains=query) |
            Q(descricao_problema__icontains=query) |
            Q(tipo_problema__nome__icontains=query) |
            Q(clientes__nome__icontains=query) |
            Q(clientes__email__icontains=query)
        ).distinct()
        resultados.append({
            "tipo": "Protocolos",
            "itens": protocolos_resultados
        })

        # Busca em Clientes
        clientes_resultados = Cliente.objects.filter(
            Q(nome__icontains=query) |
            Q(email__icontains=query)
        ).distinct()
        resultados.append({
            "tipo": "Clientes",
            "itens": clientes_resultados
        })

        # Busca em Tipos de Problemas
        tipos_problemas_resultados = TipoProblema.objects.filter(
            Q(nome__icontains=query) |
            Q(descricao__icontains=query)
        ).filter(ativo=True).distinct()
        if tipos_problemas_resultados:
            resultados.append({
                "tipo": "Tipos de Problemas",
                "itens": tipos_problemas_resultados
            })

    context = {
        "query": query,
        "resultados": resultados
    }
    return render(request, "protocolos/busca_global.html", context)

@login_required
def exportar_protocolos_csv(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = "attachment; filename=\"protocolos.csv\""

    writer = csv.writer(response)
    writer.writerow([
        "Número", "Status", "Tipo de Problema", "BUIC Dispositivo", 
        "Descrição do Problema", "Usuário Criador", "Data de Criação", "Data de Finalização"
    ])

    protocolos = Protocolo.objects.all().order_by("numero")
    for protocolo in protocolos:
        writer.writerow([
            protocolo.numero,
            protocolo.get_status_display(),
            protocolo.tipo_problema.nome,
            protocolo.buic_dispositivo,
            protocolo.descricao_problema,
            protocolo.usuario_criador.username,
            protocolo.data_criacao.strftime("%d/%m/%Y %H:%M"),
            protocolo.data_finalizacao.strftime("%d/%m/%Y %H:%M") if protocolo.data_finalizacao else "",
        ])

    return response

@login_required
def filtrar_protocolos(request):
    """View para filtrar protocolos por tipo de problema"""
    tipo_problema_id = request.GET.get('tipo_problema')
    status = request.GET.get('status')
    
    protocolos = Protocolo.objects.all()
    
    if tipo_problema_id:
        protocolos = protocolos.filter(tipo_problema_id=tipo_problema_id)
    
    if status:
        protocolos = protocolos.filter(status=status)
    
    protocolos = protocolos.order_by('-data_criacao')
    
    # Obter todos os tipos de problemas para o filtro
    tipos_problemas = TipoProblema.objects.filter(ativo=True).order_by('nome')
    
    context = {
        'protocolos': protocolos,
        'tipos_problemas': tipos_problemas,
        'tipo_problema_selecionado': int(tipo_problema_id) if tipo_problema_id else None,
        'status_selecionado': status,
    }
    
    return render(request, 'protocolos/filtrar_protocolos.html', context)
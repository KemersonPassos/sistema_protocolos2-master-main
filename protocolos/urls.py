from django.urls import path
from . import views

urlpatterns = [
    path("dashboard/", views.dashboard, name="dashboard"),
    path("novo_protocolo/", views.novo_protocolo, name="novo_protocolo"),
    path("adicionar_cliente/", views.adicionar_cliente, name="adicionar_cliente"),
    path("adicionar_tipo_problema/", views.adicionar_tipo_problema, name="adicionar_tipo_problema"),
    path("filtrar_protocolos/", views.filtrar_protocolos, name="filtrar_protocolos"),
    path("busca/", views.busca_global, name="busca_global"),
    path("exportar_csv/", views.exportar_protocolos_csv, name="exportar_protocolos_csv"),
]
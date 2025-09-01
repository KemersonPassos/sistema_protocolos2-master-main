from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect

def redirect_to_dashboard(request):
    return redirect('dashboard')

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("protocolos.urls")),  # Remove o prefixo protocolos/
    path("logout/", auth_views.LogoutView.as_view(next_page="/admin/login/"), name="logout"),
]
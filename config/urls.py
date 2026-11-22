from django.urls import path
from django.contrib import admin
from django.http import HttpResponse
from django.urls import include, path
from filmes.views import cadastrar_usuario, entrar_usuario, minha_conta


def inicio(request):
    return HttpResponse("Bem-vindo ao Claquete!")


urlpatterns = [
    path("", inicio, name="inicio"),
    path("admin/", admin.site.urls),
    path("movies/", include("filmes.urls")),
    path("auth/register/", cadastrar_usuario, name="cadastrar_usuario"),
    path("auth/login/", entrar_usuario, name="entrar_usuario"),
    path("users/me/", minha_conta, name="minha_conta"),
]
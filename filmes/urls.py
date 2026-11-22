from django.urls import path
from . import views

urlpatterns = {
    path("", views.lista_filmes, name="lista_filme"),
    path("<int:filme_id>/", views.detalhe_filme, name="detalhe_filme"),
}
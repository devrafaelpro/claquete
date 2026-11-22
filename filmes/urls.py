from django.urls import path
from . import views

urlpatterns = [
    path("", views.lista_filmes, name="listar_filmes"),
    path("<int:filme_id>/", views.detalhe_filme, name="detalhe_filme"),
    path("<int:filme_id>/ratings/", views.avaliacoes_filme, name="avaliacoes_filme"),
    path("<int:filme_id>/comments/", views.comentarios_filme, name="comentarios_filme"),
]
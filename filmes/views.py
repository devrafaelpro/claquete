from django.shortcuts import render
from django.http import JsonResponse
from .models import Filme

import json

from django.core.exceptions import ValidationError
from django.views.decorators.http import require_http_methods



@require_http_methods(["GET", "POST"])
def lista_filmes(request):
    if request.method == "POST":
        return cadastrar_filme(request)

    busca = request.GET.get("q", "").strip()
    filmes = Filme.objects.order_by("titulo", "id")

    if busca:
        filmes = filmes.filter(titulo__icontains=busca)

    dados = filmes.values("id", "titulo", "ano", "genero", "sinopse")
    return JsonResponse(list(dados), safe=False)

def cadastrar_filme(request):
    try:
        dados = json.loads(request.body)
    except ValueError:
        return JsonResponse({"erro": "Envie um JSON válido."}, status=400)

    if not isinstance(dados, dict):
        return JsonResponse({"erro": "Envie os dados do filme em um objeto JSON."}, status=400)

    filme = Filme(
        titulo=dados.get("titulo"),
        ano=dados.get("ano"),
        genero=dados.get("genero"),
        sinopse=dados.get("sinopse"),
    )

    try:
        filme.full_clean()
    except ValidationError as erro:
        return JsonResponse({"erros": erro.message_dict}, status=400)

    filme.save()
    return JsonResponse({"id": filme.id, "titulo": filme.titulo}, status=201)

@require_http_methods(["GET"])
def detalhe_filme(request, filme_id):
    try:
        filme = Filme.objects.get(pk=filme_id)
    except Filme.DoesNotExist:
        return JsonResponse({"erro": "Filme não encontrado."}, status=404)

    return JsonResponse({
        "id": filme.id,
        "titulo": filme.titulo,
        "ano": filme.ano,
        "genero": filme.genero,
        "sinopse": filme.sinopse,
    })
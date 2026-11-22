from django.shortcuts import render
from django.http import JsonResponse
from .models import Filme

import json

from django.core.exceptions import ValidationError
from django.views.decorators.http import require_http_methods

from django.contrib.auth import authenticate, get_user_model, login
from django.contrib.auth.password_validation import validate_password
from django.db import IntegrityError, transaction

from .forms import CadastroForm
from .models import Perfil




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

@require_http_methods(["POST"])
def cadastrar_usuario(request):
    try:
        dados = json.loads(request.body)
    except ValueError:
        return JsonResponse({"erro": "Envie um JSON válido."}, status=400)

    if not isinstance(dados, dict):
        return JsonResponse(
            {"erro": "Envie os dados da conta em um objeto."},
            status=400,
        )

    formulario = CadastroForm(dados)
    if not formulario.is_valid():
        return JsonResponse({"erros": formulario.errors}, status=400)

    campos = formulario.cleaned_data
    email = campos["email"].lower()
    senha = campos["senha"]

    Usuario = get_user_model()
    usuario = Usuario(username=email, email=email, first_name=campos["nome"])

    try:
        validate_password(senha, user=usuario)
    except ValidationError as erro:
        return JsonResponse({"erros": {"senha": erro.messages}}, status=400)

    usuario.set_password(senha)

    try:
        with transaction.atomic():
            usuario.save()
            Perfil.objects.create(
                usuario=usuario,
                genero_preferido=campos["genero_preferido"],
            )
    except IntegrityError:
        if Usuario.objects.filter(username=email).exists():
            return JsonResponse({"erro": "Este e-mail já está cadastrado."}, status=409)
        raise

    return JsonResponse({"id": usuario.pk, "nome": usuario.first_name}, status=201)

@require_http_methods(["POST"])
def entrar_usuario(request):
    try:
        dados = json.loads(request.body)
    except ValueError:
        return JsonResponse({"erro": "Envie um JSON válido."}, status=400)

    if not isinstance(dados, dict):
        return JsonResponse({"erro": "Envie um objeto com e-mail e senha."}, status=400)

    email = dados.get("email")
    senha = dados.get("senha")

    if not isinstance(email, str) or not email.strip():
        return JsonResponse({"erro": "Informe o e-mail."}, status=400)

    if not isinstance(senha, str) or not senha:
        return JsonResponse({"erro": "Informe a senha."}, status=400)

    usuario = authenticate(
        request,
        username=email.strip().lower(),
        password=senha,
    )

    if usuario is None:
        return JsonResponse({"erro": "E-mail ou senha inválidos."}, status=401)

    login(request, usuario)
    return JsonResponse({"id": usuario.pk, "nome": usuario.first_name})
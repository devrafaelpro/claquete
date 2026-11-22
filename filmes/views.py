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

from django.db.models import Avg, Count
from .models import Avaliacao




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

@require_http_methods(["GET"])
def minha_conta(request):
    usuario = request.user

    if not usuario.is_authenticated:
        return JsonResponse({"erro": "Faça login para acessar sua conta."}, status=401)

    perfil = Perfil.objects.filter(usuario=usuario).first()

    return JsonResponse({
        "id": usuario.pk,
        "nome": usuario.first_name,
        "email": usuario.email,
        "genero_preferido": perfil.genero_preferido if perfil else "",
    })

@require_http_methods(["GET", "POST"])
def avaliacoes_filme(request, filme_id):
    try:
        filme = Filme.objects.get(pk=filme_id)
    except Filme.DoesNotExist:
        return JsonResponse({"erro": "Filme não encontrado."}, status=404)

    if request.method == "GET":
        # "avaliacoes" é o related_name que você colocou no modelo.
        resumo = filme.avaliacoes.aggregate(media=Avg("nota"), total=Count("id"))

        minha_nota = None
        if request.user.is_authenticated:
            minha_nota = (
                filme.avaliacoes.filter(usuario=request.user)
                .values_list("nota", flat=True)
                .first()
            )

        return JsonResponse({
            "media": resumo["media"],
            "total": resumo["total"],
            "minha_nota": minha_nota,
        })

    if not request.user.is_authenticated:
        return JsonResponse({"erro": "Faça login para avaliar."}, status=401)

    try:
        dados = json.loads(request.body)
    except ValueError:
        return JsonResponse({"erro": "Envie um JSON válido."}, status=400)

    nota = dados.get("nota") if isinstance(dados, dict) else None
    if type(nota) is not int or not 1 <= nota <= 5:
        return JsonResponse({"erro": "Envie uma nota inteira de 1 a 5."}, status=400)

    # Usuário e filme identificam a avaliação. Só o valor da nota muda.
    avaliacao, criada = Avaliacao.objects.update_or_create(
        usuario=request.user,
        filme=filme,
        defaults={"nota": nota},
    )

    return JsonResponse({"nota": avaliacao.nota}, status=201 if criada else 200)

@require_http_methods(["GET", "POST"])
def comentarios_filme(request, filme_id):
    try:
        filme = Filme.objects.get(pk=filme_id)
    except Filme.DoesNotExist:
        return JsonResponse({"erro": "Filme não encontrado."}, status=404)

    if request.method == "GET":
        # Busca os comentários deste filme, do mais antigo ao mais recente.
        # select_related carrega o autor junto com cada comentário.
        comentarios = filme.comentarios.select_related("usuario").order_by("criado_em", "id")

        dados = [
            {
                "id": comentario.id,
                "autor": comentario.usuario.first_name,
                "texto": comentario.texto,
                "criado_em": comentario.criado_em,
            }
            for comentario in comentarios
        ]
        return JsonResponse(dados, safe=False)

    if not request.user.is_authenticated:
        return JsonResponse({"erro": "Faça login para comentar."}, status=401)

    try:
        dados = json.loads(request.body)
    except ValueError:
        return JsonResponse({"erro": "Envie um JSON válido."}, status=400)

    texto = dados.get("texto") if isinstance(dados, dict) else None
    if not isinstance(texto, str) or not texto.strip():
        return JsonResponse({"erro": "Escreva um comentário."}, status=400)

    # O filme vem da URL e o autor vem da sessão de login.
    comentario = filme.comentarios.create(
        usuario=request.user,
        texto=texto.strip(),
    )

    return JsonResponse({
        "id": comentario.id,
        "autor": request.user.first_name,
        "texto": comentario.texto,
        "criado_em": comentario.criado_em,
    }, status=201)
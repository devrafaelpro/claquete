from django.db import models
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator

class Filme(models.Model):
    titulo = models.CharField(max_length=200)
    ano = models.PositiveIntegerField()
    genero = models.CharField(max_length=100)
    sinopse = models.TextField()
    capa = models.ImageField(upload_to="capas/", blank=True)

class Perfil(models.Model):
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="perfil",
    )
    genero_preferido = models.CharField(max_length=100, blank=True)

class Avaliacao(models.Model):
    # Cada avaliação pertence a um usuário e a um filme.
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    filme = models.ForeignKey(Filme, on_delete=models.CASCADE, related_name="avaliacoes")

    # Os validadores permitem mostrar uma mensagem quando a nota sai da escala.
    nota = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )

    class Meta:
        constraints = [
            # O mesmo usuário pode avaliar vários filmes, uma vez cada.
            models.UniqueConstraint(
                fields=["usuario", "filme"],
                name="avaliacao_unica_por_usuario_e_filme",
            ),
            # O banco também garante que toda nota fique entre 1 e 5.
            models.CheckConstraint(
                condition=models.Q(nota__gte=1, nota__lte=5),
                name="avaliacao_nota_entre_1_e_5",
            ),
        ]

    def __str__(self):
        return self.titulo
    
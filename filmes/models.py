from django.db import models
from django.conf import settings

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

    def __str__(self):
        return self.titulo
    
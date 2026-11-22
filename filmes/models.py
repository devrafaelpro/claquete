from django.db import models


class Filme(models.Model):
    titulo = models.CharField(max_length=200)
    ano = models.PositiveIntegerField()
    genero = models.CharField(max_length=100)
    sinopse = models.TextField()
    capa = models.ImageField(upload_to="capas/", blank=True)

    def __str__(self):
        return self.titulo
    
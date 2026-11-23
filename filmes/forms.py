from django import forms
from .models import Filme

class CadastroForm(forms.Form):
    nome = forms.CharField(max_length=150)
    email = forms.EmailField(max_length=150)
    senha = forms.CharField(strip=False)
    genero_preferido = forms.CharField(max_length=100, required=False)

class FilmeForm(forms.ModelForm):
    class Meta:
        # O Django usa os campos do modelo para validar os dados recebidos.
        model = Filme
        fields = ["titulo", "ano", "genero", "sinopse", "capa"]
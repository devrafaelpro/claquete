from django import forms

class CadastroForm(forms.Form):
    nome = forms.CharField(max_length=150)
    email = forms.EmailField(max_length=150)
    senha = forms.CharField(strip=False)
    genero_preferido = forms.CharField(max_length=100, required=False)
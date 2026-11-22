from django.shortcuts import render
from django.http import JsonResponse

def lista_filmes(request):
    return JsonResponse([], safe=False)

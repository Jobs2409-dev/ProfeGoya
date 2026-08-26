# core/views.py
from django.http import JsonResponse
from django.shortcuts import render


def health_check(request):
    return JsonResponse({'status': 'ok', 'service': 'Mi Proyecto API. Soy Jonathan.'})


from django.http import JsonResponse
from django.shortcuts import render


def health_check(request):
    """
    Health check endpoint for Docker, AWS, Render, Fly.io, and load balancer probes.
    """
    return JsonResponse({'status': 'healthy', 'service': 'project-finder'})

import logging
from django.shortcuts import render
from django.http import HttpRequest

logger = logging.getLogger("monitoring")


def test(request: HttpRequest):
    logger.info("Monitoring index page")
    print("Monitoring index page")
    return render(request, "index.html")


# views.py (optional - if you want separate view)
from django.http import JsonResponse
from .utils import get_system_info


def system_info_api(request):
    """Standalone API endpoint for system information"""
    return JsonResponse(get_system_info())

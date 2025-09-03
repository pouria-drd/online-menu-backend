import logging
from django.shortcuts import render
from django.http import HttpRequest

logger = logging.getLogger("monitoring")

# Create your views here.


def test(request: HttpRequest):
    logger.info("Monitoring index page")
    print("Monitoring index page")
    return render(request, "index.html")

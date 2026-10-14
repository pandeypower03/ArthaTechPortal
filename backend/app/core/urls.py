from django.contrib import admin
from django.http import JsonResponse
from django.urls import path, include

def health(request):
    return JsonResponse({"status": "ok"})

urlpatterns = [
    path("api/health/", health),
    path("api/accounts/", include("accounts.urls")),
    path("api/organisations/", include("organisations.urls")),

]
from django.contrib import admin
from django.http import JsonResponse
from django.urls import path, include

def health(request):
    return JsonResponse({"status": "ok"})

urlpatterns = [
    path("api/health/", health),
    path("api/accounts/", include("accounts.urls")),
    path("api/morning-brief/", include("morning_brief.urls")),
    path("api/people/", include("people.urls")),
    path("api/goals/", include("goals.urls")),
    path("api/pulse/", include("pulse.urls")),
    path("api/inbox/", include("inbox.urls")),
    path("api/decisions/", include("decisions.urls")),
    path("api/meetings/", include("meetings.urls")),
]
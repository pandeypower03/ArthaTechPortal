from django.urls import path
from .views import HouseListView, UploadView, CreateHouseView, RemoveView, AuditLogListView, UpdateHouseView, AddToHouseView

urlpatterns = [
    path("", HouseListView.as_view()),
    path("upload/", UploadView.as_view()),
    path("createhouse/", CreateHouseView.as_view()),
    path("update/<int:house_id>/", UpdateHouseView.as_view()),
    path("remove/<str:kind>/<int:item_id>/", RemoveView.as_view()),
    path("add/<int:house_id>/", AddToHouseView.as_view()),
    path("audit-log/", AuditLogListView.as_view()),
]
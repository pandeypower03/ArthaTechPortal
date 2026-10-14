from django.urls import path
from .views import HouseListView, UploadView, CreateHouseView, RemoveView

urlpatterns = [
    path("", HouseListView.as_view()),
    path("upload/", UploadView.as_view()),
    path("createhouse/", CreateHouseView.as_view()),
    path("remove/<str:kind>/<int:item_id>/", RemoveView.as_view()),
]
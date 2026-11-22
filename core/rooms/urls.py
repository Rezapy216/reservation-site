from django.urls import path, include
from . import views

app_name = "rooms"
urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("rooms-list/", views.RoomsListView.as_view(), name="room-list"),
    path("room-detail/<int:pk>/", views.RoomDetailView.as_view(), name="room-detail"),
    path("api/v1/", include("rooms.api.v1.urls", "api-v1")),
]

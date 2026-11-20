from django.urls import path, include
from . import views

app_name = "booking"
urlpatterns = [
    path(
        "booking/<int:room_pk>/create/",
        views.BookingCreateView.as_view(),
        name="booking_create",
    ),
    path("api/v1/", include("bookings.api.v1.urls")),
]

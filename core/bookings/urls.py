from django.urls import path
from . import views

app_name = 'booking'
urlpatterns = [
    path('booking/<int:room_pk>/create/', views.BookingCreateView.as_view(), name='booking_create')
    
]
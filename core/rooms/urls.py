from django.urls import path
from django.views.generic import TemplateView
from . import views

app_name = 'rooms'
urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('rooms-list/', views.RoomsListView.as_view(), name='room_list'),
    path('room-detail/<pk>/', views.RoomDetailView.as_view(), name='room_detail'),
    
    
]

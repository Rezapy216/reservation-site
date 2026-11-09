from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.views.generic import ListView, DetailView
from .models import Room

class HomeView(TemplateView):
    '''
    a simple class based view to show home page 
    '''
    
    template_name = 'rooms/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['rooms'] = Room.objects.prefetch_related('pictures').all()
        return context
        
class RoomsListView(ListView):
    '''
    a simple view for returning rooms from model    
    '''
    
    model = Room
    context_object_name = 'rooms'
    ordering = "-pay_per_night"
    
class RoomDetailView(DetailView):
    model = Room
    
 
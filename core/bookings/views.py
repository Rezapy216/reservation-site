from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.core.exceptions import ValidationError
from .models import Booking
from .forms import BookingForm
from rooms.models import Room




class BookingCreateView(LoginRequiredMixin, CreateView):
    model = Booking
    form_class = BookingForm
    template_name = 'bookings/booking_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['room'] = get_object_or_404(Room, pk=self.kwargs['room_pk'])
        return context
    
    def form_valid(self, form):
        
        # creating instance first without saving
        booking = form.save(commit=False)
        
        # set the guest
        booking.guest = self.request.user
        
        # find the room whit address parameter like pk or room_id
        booking.room = get_object_or_404(Room, pk=self.kwargs['room_pk'])
        
        try: 
            booking.save()
        except ValidationError as e:
            form.add_error(None, e)
            return self.form_invalid(form)
        
        return super().form_valid(form)
    
    def get_success_url(self):
       return reverse_lazy('rooms:home')
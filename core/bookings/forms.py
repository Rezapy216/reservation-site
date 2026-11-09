from django.forms import ModelForm, DateInput
from .models import Booking
class BookingForm(ModelForm):

    class Meta:
        model = Booking
        fields = ["date_in", "date_out", "number_of_people"]
        widgets = {
            'date_in': DateInput(attrs={'type': 'date'}),
            'date_out': DateInput(attrs={'type': 'date'}),
        }
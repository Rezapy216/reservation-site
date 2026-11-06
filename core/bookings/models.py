from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import F, Q

from rooms.models import Room


class Booking(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        EXPIRED = "expired", "Expired"
        CANCELLED = "cancelled", "Cancelled"

    room = models.ForeignKey(
        Room, on_delete=models.PROTECT, related_name="bookings"
    )
    guest = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="bookings"
    )
    date_in = models.DateField()
    date_out = models.DateField()
    number_of_people = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)]
    )
    price_per_night = models.DecimalField(
        max_digits=12, decimal_places=0, editable=False
    )
    total_price = models.DecimalField(
        max_digits=12, decimal_places=0, editable=False
    )
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.PENDING
    )
    pending_exp_time = models.DateTimeField(null=True, blank=True)
    created_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_time"]
        constraints = [
            models.CheckConstraint(
                condition=Q(date_out__gt=F("date_in")),
                name="booking_date_out_after_date_in",
            ),
        ]

    def __str__(self):
        return f"{self.room} | {self.date_in} -> {self.date_out} | {self.get_status_display()}"

    @property
    def nights(self):
        return (self.date_out - self.date_in).days

    def clean(self):
        if self.date_in and self.date_out and self.date_out <= self.date_in:
            raise ValidationError("Check-out date must be after check-in date.")
        if (
            self.room_id
            and self.number_of_people
            and self.number_of_people > self.room.permitted_guests):
            raise ValidationError("Number of people exceeds the room capacity.")
        
        if self.room_id and self.date_in and self.date_out:
            overlapping_bookings = Booking.objects.filter(
                room_id=self.room_id,
                date_in__lt=self.date_out,  
                date_out__gt=self.date_in,   
                status__in=[self.Status.PENDING, self.Status.CONFIRMED], 
            )
        if self.pk:
            overlapping_bookings = overlapping_bookings.exclude(pk=self.pk)
        
        if overlapping_bookings.exists():
                raise ValidationError("This room is already booked for the selected dates.")
            

    def save(self, *args, **kwargs):
        if self._state.adding:  
            self.price_per_night = self.room.pay_per_night
            self.total_price = self.price_per_night * self.nights
        super().save(*args, **kwargs)
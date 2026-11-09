from datetime import timedelta

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import F, Q
from django.utils import timezone

from rooms.models import Room

PENDING_HOLD_MINUTES = 30  # مدت نگه‌داشتن اتاق برای پرداخت


class Booking(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        EXPIRED = "expired", "Expired"
        CANCELLED = "cancelled", "Cancelled"

    room = models.ForeignKey(Room, on_delete=models.PROTECT, related_name="bookings")
    guest = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="bookings"
    )
    date_in = models.DateField()
    date_out = models.DateField()
    number_of_people = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])
    pay_per_night = models.DecimalField(max_digits=12, decimal_places=2, editable=False)
    total_price = models.DecimalField(max_digits=12, decimal_places=2, editable=False)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.PENDING)
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_date"]
        constraints = [
            models.CheckConstraint(
                condition=Q(date_out__gt=F("date_in")),
                name="booking_date_out_after_date_in",
            ),
        ]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("room__hotel", "guest")

    @property
    def nights(self):
        return (self.date_out - self.date_in).days

    def clean(self):
        if not (self.date_in and self.date_out):
            return
        if self.date_out <= self.date_in:
            raise ValidationError("date out must be later than date in")

        if not self.room_id:
            return

        if self._state.adding and self.date_in < timezone.localdate():
            raise ValidationError("check-in date is in the past")

        if self.number_of_people and self.number_of_people > self.room.permitted_guests:
            raise ValidationError("number of people exceeds the room capacity")

        
        if self.status not in (self.Status.PENDING, self.Status.CONFIRMED):
            return

        limit = timezone.now() - timedelta(minutes=PENDING_HOLD_MINUTES)
        blocking = Q(status=self.Status.CONFIRMED) | Q(
            status=self.Status.PENDING, created_date__gt=limit
        )
        overlapping = Booking.objects.filter(
            blocking,
            room_id=self.room_id,
            date_out__gt=self.date_in,
            date_in__lt=self.date_out,
        )
        if self.pk:
            overlapping = overlapping.exclude(pk=self.pk)

        if overlapping.filter(status=self.Status.CONFIRMED).exists():
            raise ValidationError("room already booked in that timeline")
        if overlapping.exists():
            raise ValidationError("room is pending by another user")

    def save(self, *args, **kwargs):
        if self._state.adding:
            self.pay_per_night = self.room.pay_per_night 
        if self.date_in and self.date_out:
            self.total_price = self.nights * self.pay_per_night
        self.full_clean()
        super().save(*args, **kwargs)
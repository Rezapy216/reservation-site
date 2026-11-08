from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from bookings.models import PENDING_HOLD_MINUTES, Booking


class Command(BaseCommand):
    help = "Mark old pending bookings as expired"

    def handle(self, *args, **kwargs):
        limit = timezone.now() - timedelta(minutes=PENDING_HOLD_MINUTES)
        count = Booking.objects.filter(
            status=Booking.Status.PENDING,
            created_date__lt=limit,
        ).update(status=Booking.Status.EXPIRED)
        self.stdout.write(f"Successfully expired {count} bookings.")
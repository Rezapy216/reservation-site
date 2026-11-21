from django.db import models
from core import settings
from django.core.validators import MaxValueValidator, MinValueValidator


class Room(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=300, default="unnamed")
    is_active = models.BooleanField(default=True)
    amenities = models.ManyToManyField("Amenity")
    pay_per_night = models.DecimalField(max_digits=7, decimal_places=2)
    permitted_guests = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(50)]
    )
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.owner.name} ,{self.name}"


class Amenity(models.Model):
    name = models.CharField(max_length=80)

    def __str__(self):
        return f"{self.name}"


class Picture(models.Model):
    image = models.ImageField(upload_to="rooms/", null=True, blank=True)
    room = models.ForeignKey(
        Room, on_delete=models.CASCADE, blank=True, null=True, related_name="pictures"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Picture for {self.room}"

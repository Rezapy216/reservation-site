from django.db import models
from core import settings


class Room(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amenities = models.ManyToManyField("Amenity") 
    pay_per_night = models.DecimalField()
    permitted_guests = models.DecimalField()
    
    def __str__(self):
        return f'{self.owner.name} ,{self.owner}'
    
    
class Amenity(models.Model):
    name = models.CharField(max_length=80)
    
    def __str__(self):
           def __str__(self):
            return f"Room {self.id} - {self.owner.name}"

    
class Picture(models.Model):
    image = models.ImageField(upload_to="rooms/", null=True, blank=True)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, blank=True, null=True, related_name='pictures')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Picture for {self.room}"

from datetime import datetime

from django.test import TestCase

from ..models import Room, Amenity
from accounts.models import User


class TestRoomModel(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user('09129129120','reza1385')
        self.amenity = Amenity.objects.create(name='test-amenity')
    def test_create_room_with_valid_data(self):
        room = Room.objects.create(
            owner = self.user,
            name = 'test room',
            pay_per_night = 100,
            permitted_guests = 4,
            created_date = datetime.now() 
            )
        
        
        room.amenities.set([self.amenity])
        
        self.assertTrue(Room.objects.filter(pk = room.id))
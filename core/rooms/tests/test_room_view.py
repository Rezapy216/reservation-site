from django.test import TestCase, Client
from django.urls import reverse
from datetime import datetime

from ..models import Room
from accounts.models import User

class TestRoomView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('09129129120','reza1385')
        self.room = Room.objects.create(
            owner = self.user,
            name = 'test room',
            pay_per_night = 100,
            permitted_guests = 4,
            created_date = datetime.now() 
            )
        
    def test_room_url_successful_response(self):
        url = reverse('rooms:home')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='rooms/home.html')
        self.assertTrue(str(response.content).find('room'))
        
    def test_room_detail_logged_in_response(self):
        self.client.force_login(self.user)
        url = reverse('rooms:room_detail', kwargs={'pk':self.room.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


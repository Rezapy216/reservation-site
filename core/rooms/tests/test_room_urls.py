from django.test import TestCase, SimpleTestCase
from django.urls import reverse, resolve

from ..views import HomeView, RoomDetailView, RoomsListView

class TestUrl(SimpleTestCase):
    def test_room_index_url_resolve(self):
        url = reverse('rooms:home')
        # print(resolve(url).func)
        self.assertEqual(resolve(url).func.view_class.__name__, HomeView.__name__)
        
    def test_rooms_list_url_resolve(self):
        url = reverse('rooms:rooms-list')
        self.assertEqual(resolve(url).func.view_class.__name__, RoomsListView.__name__)   
        
    def test_room_detail_url_resolve(self):
        url = reverse('rooms:room-detail', kwargs={'pk':1})
        self.assertEqual(resolve(url).func.view_class.__name__, RoomDetailView.__name__)
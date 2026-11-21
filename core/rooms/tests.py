from django.test import TestCase, SimpleTestCase
from django.urls import reverse, resolve

from .views import HomeView


class TestUrl(SimpleTestCase):
    def test_blog_index_url_resolve(self):
        url = reverse("rooms:home")
        self.assertEqual(resolve(url).func.view_class, HomeView)

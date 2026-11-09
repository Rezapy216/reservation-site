from django.urls import path
from . import views
urlpatterns = [
    path("test-api/", views.api_test)
]
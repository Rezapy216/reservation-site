from django.urls import path, include
from accounts.views import registration, my_profile

app_name= 'accounts'
urlpatterns = [
    path("", include("django.contrib.auth.urls")),
    path("api/v1/", include("accounts.api.v1.urls")),
    path("register/", registration, name='register'),
    path('my-profile/', my_profile, name='my-profile')
]

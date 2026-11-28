from django.urls import path, include
from accounts.views import RegistrationView, ProfileView, AccountVerifyView

app_name= 'accounts'
urlpatterns = [
    path("", include("django.contrib.auth.urls")),
    path("api/v1/", include("accounts.api.v1.urls")),
    path("register/", RegistrationView.as_view(), name='register'),
    path('my-profile/', ProfileView.as_view(), name='my-profile'),
    path("verify/", AccountVerifyView.as_view(), name="verify")
]

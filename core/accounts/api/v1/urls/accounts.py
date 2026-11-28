from django.urls import path

from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
)

from .. import views

urlpatterns = [
    path("email_test", views.TestSendEmail.as_view(), name="send-email"),
    path("registration/", views.RegistrationView.as_view(), name="registration"),
    path(
        "activation/confirm/<str:token>",
        views.ActivationApiView.as_view(),
        name="activation",
    ),
    path('activation/verify/', views.ActivationResendApiView.as_view(), name='verify'),
    # path("activation/resend/",views.ActivationResendApiView.as_view(),name="activation-resend"),
    path(
        "change-password", views.ChangePasswordApiView.as_view(), name="change-password"
    ),
    path("token/login/", views.CustomAuthToken.as_view(), name="token-login"),
    path("token/logout/", views.CustomDiscardAuthToken.as_view(), name="token-logout"),
    path("jwt/create/", views.CustomTokenObtainPairView.as_view(), name="jwt-create"),
    path("jwt/refresh/", TokenRefreshView.as_view(), name="jwt-refresh"),
    path("jwt/verify/", TokenVerifyView.as_view(), name="jwt-verify"),
]

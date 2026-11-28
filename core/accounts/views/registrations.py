from django.views.generic.base import TemplateView

class RegistrationView(TemplateView):
    template_name = "registration/register.html"

class AccountVerifyView(TemplateView):
    template_name = "registration/verify.html"
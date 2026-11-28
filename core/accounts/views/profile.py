from django.views.generic.base import TemplateView

class ProfileView(TemplateView):
    template_name = 'accounts/profile.html'
    


from django.contrib.auth import get_user_model
from rest_framework import permissions, generics

from ..serializers import ProfileSerializer

User = get_user_model()


class ProfileApiView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = User.objects.all()

    def get_object(self):
        user = self.request.user
        return user

from rest_framework import serializers

from django.contrib.auth import get_user_model

# getting the user model
User = get_user_model()


class ProfileSerializer(serializers.ModelSerializer):

    phone = serializers.CharField(max_length=11, read_only=True)

    class Meta:
        model = User
        fields = ("id", "name", "phone", "is_verified")
        read_only_fields = ("is_verified",)
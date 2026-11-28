from rest_framework import serializers

from django.contrib.auth import get_user_model

# getting the user model
User = get_user_model()


class ProfileSerializer(serializers.ModelSerializer):

    phone = serializers.CharField(max_length=11, read_only=True)

    class Meta:
        model = User
<<<<<<< HEAD
        fields = ("id", "name", "phone", "email")
=======
        fields = ("id", "name", "phone", "is_verified")
        read_only_fields = ("is_verified",)
>>>>>>> 70242492fe5cf84f0b2fdcb1ae6c9c811d86ff73

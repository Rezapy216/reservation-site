from rest_framework import serializers

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions

# getting the user model
User = get_user_model()


class RegistrationSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(max_length=255, write_only=True)

    class Meta:
        model = User
        fields = [
            "phone",
            "email",
            "name",
            "password",
            "confirm_password",
        ]

    def validate(self, attrs):
        if attrs.get("password") != attrs.get("confirm_password"):
            raise serializers.ValidationError({"detail": "passwords dose'nt match"})

        try:
            validate_password(attrs.get("password"))
        except exceptions.ValidationError as e:
            raise serializers.ValidationError({"password": list(e.messages)})
        return super().validate(attrs)

    def create(self, validated_data):
        validated_data.pop("confirm_password", None)
        return User.objects.create_user(**validated_data)


class ChangePasswordSerializer(serializers.Serializer):
    """check if new_password confirmed correctly"""

    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_new_password = serializers.CharField(required=True)

    def validate(self, attrs):

        if attrs.get("new_password") != attrs.get("confirm_new_password"):
            raise serializers.ValidationError({"detail": "passwords dose'nt match"})

        try:
            validate_password(attrs.get("new_password"))
        except exceptions.ValidationError as e:
            raise serializers.ValidationError({"new_password": list(e.messages)})

        return super().validate(attrs)

class ActivationResendSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=11 ,required=True)
    def validate(self, attrs):
        phone = attrs.get('phone')
        
        try:
            user_obj = User.objects.get(phone=phone)
        except User.DoesNotExist:
            raise serializers.ValidationError({'details': 'user dose not exist'})
        
        if user_obj.is_verified:
            raise serializers.ValidationError({'details': 'user is already activated and verified'})
        
        attrs['user'] = user_obj
        return super().validate(attrs)
            
            
            
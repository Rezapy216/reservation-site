from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator

phone_validator = RegexValidator(regex=r"\A09[0-9]{9}\Z",
                                 message="phone number must start with 09 and have 11 digits(en)")

class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """
    def create_user(self, phone, password, **extra_fields):
        if not phone:
            raise ValueError(_("The Phone number must be set or invalid"))

        phone_validator(phone)
        
        if extra_fields.get('email'):
            extra_fields["email"] = self.normalize_email(extra_fields['email'])
        
        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save()
        
        return user
        
        
    def create_superuser(self, phone, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        phone_validator(phone)
        
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
        return self.create_user(phone, password, **extra_fields)    


class User(AbstractBaseUser, PermissionsMixin):
    phone = models.CharField(max_length=11, unique=True)
    email = models.EmailField(max_length=255, unique=True, null=True, blank=True)
    name = models.CharField(max_length=100)
    is_host = models.CharField(default='guest')
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    
    objects = CustomUserManager()
    
    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = ['name']
    
    def __str__(self):
        return f"{self.name}: {self.phone}"
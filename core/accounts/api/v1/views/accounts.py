from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.conf import settings

from rest_framework import permissions, status, views, generics
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from mail_templated import EmailMessage
from jwt import ExpiredSignatureError, InvalidSignatureError

from ...utils import EmailThread
from ..serializers import (
    RegistrationSerializer,
    ChangePasswordSerializer,
    ActivationResendSerializer
)

import jwt

User = get_user_model()


class RegistrationView(generics.GenericAPIView):
    serializer_class = RegistrationSerializer

    def post(self, request, *args, **kwargs):

        serializer = RegistrationSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            email = serializer.validated_data["email"]
            data = {"email": email}
            user_obj = get_object_or_404(User, email=email)
            token = self.get_tokens_for_user(user_obj)
            email_obj = EmailMessage(
                "email/activation_email.tpl",
                {"token": token},
                "admin@admin.com",
                to=[email],
            )

            EmailThread(email_obj).start()

            return Response({'detail': {
                '''a verification emil sended to your email pleas check your email\n
                for booking or hosting a room please verify your account
                ''',
                # data
                }
            },
            status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_tokens_for_user(self, user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)


class ChangePasswordApiView(generics.GenericAPIView):

    model = User
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def put(self, request):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():

            if not self.object.check_password(serializer.data.get("old_password")):
                return Response(
                    {"old_password": ["Wrong password."]},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()

            return Response(
                {"detail": "password changed successfully"}, status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class ActivationApiView(views.APIView):

    def get(self, request, token, *args, **kwargs):

        try:
            token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id = token.get("user_id")

        except ExpiredSignatureError:
            return Response(
                {"details": "Token has been expired"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except InvalidSignatureError:
            return Response(
                {"details": "Token is not valid"}, status=status.HTTP_400_BAD_REQUEST
            )

        user_obj = User.objects.get(pk=user_id)
        if not user_obj.is_verified:
            user_obj.is_verified = True
            user_obj.save()
        else:
            return Response({"details": "user is already verified"})

        return Response({"confirmed": token})


class ActivationResendApiView(generics.GenericAPIView):
    
    serializer_class = ActivationResendSerializer
    
    def post(self, request, *args, **kwargs):
        
        serializer = ActivationResendSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_obj = serializer.validated_data['user']
        token = self.get_token_for_user(user_obj)
        email_obj = EmailMessage(
            'email/activation_email.tpl',
            {'token': token},
            '9123456789',
            to=[user_obj.phone],    
        ) 
        
        EmailThread(email_obj).start()
        return Response(
            {"details": "user activation resend successfully"},
            status=status.HTTP_200_OK,
        )
     
        
    def get_token_for_user(self, user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)


class TestSendEmail(generics.GenericAPIView):
    serializer_class = None

    def get(self, request):
        phone = "09123456789"
        user_obj = get_object_or_404(User, phone=phone)
        token = self.get_tokens_for_user(user_obj)
        email_obj = EmailMessage(
            "email/hello.tpl", {"token": token}, "9123456789", to=["09123456789"]
        )

        EmailThread(email_obj).start()

        return Response("email sent")

    def get_tokens_for_user(self, user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)

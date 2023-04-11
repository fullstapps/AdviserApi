from django.shortcuts import render

# Create your views here.
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework import permissions,serializers, exceptions, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from advmessages.services import AdvMessagesService
from authentication.backends import EmailAuthBackend


from django.contrib.auth.models import User
from .models import Profile

class SignUpView(APIView):
    permission_classes = (permissions.AllowAny,)

    class InputSerializer(serializers.Serializer):
        email = serializers.EmailField()
        first_name = serializers.CharField(max_length=100)
        last_name = serializers.CharField(max_length=100)
        password = serializers.CharField()

        def validate_email(self, data):
            email = data.lower()

            if User.objects.filter(email=email).exists():
                msg = "Ya existe un usuario registrado con este correo electrónico."
                raise exceptions.ValidationError(msg)

            return email

        def validate(self, data):
            first_name = data['first_name']
            last_name = data['last_name']
            username = '%s.%s' % (first_name.lower(), last_name.lower())
            username = '{:.29}'.format(username)
            counter = User.objects.filter(first_name=first_name, last_name=last_name).count()
            if counter > 0:
                username += '%s' % (counter + 1)
            data['username'] = username
            return data

    def post(self, request):
        serializer_data = self.InputSerializer(data=request.data)
        serializer_data.is_valid(raise_exception=True)
        user = User.objects.create_user(
            username=serializer_data.validated_data['username'],
            email=serializer_data.validated_data['email'].lower(),
            password=serializer_data.validated_data['password'],
            first_name=serializer_data.validated_data['first_name'],
            last_name=serializer_data.validated_data['last_name']
        )
        profile = Profile.objects.create(
            user=user,
        )

        return Response(
            data={'code': 'ok'},
            status=status.HTTP_200_OK
        )

class LoginView(APIView):
    permission_classes = (permissions.AllowAny,)

    class InputSerializer(serializers.Serializer):
        email = serializers.EmailField(max_length=100)
        password = serializers.CharField(max_length=150)

        def validate(self, data):
            email = data.get('email').lower()
            password = data.get('password')
            backend = EmailAuthBackend()

            if email and password:
                user = backend.authenticate(email=email, password=password)

                if user:
                    if not user.is_active:
                        msg = 'User account is disabled.'
                        raise exceptions.ValidationError(msg)
                else:
                    msg = 'Unable to log in with provided credentials.'
                    raise exceptions.ValidationError(msg)
            else:
                msg = 'Must include "email" and "password".'
                raise exceptions.ValidationError(msg)

            data['user'] = user
            return data

    def post(self, request):
        serializer_data = self.InputSerializer(data=request.data)
        serializer_data.is_valid(raise_exception=True)
        user = serializer_data.validated_data['user']
        Token.objects.get_or_create(user=user)
        profile = Profile.objects.get(user=user)

        data = {
            'token': user.auth_token.key,
        }

        return Response(
            data=data,
            status=status.HTTP_200_OK
        )


class ProfileView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    class InputSerializer(serializers.Serializer):
        bio = serializers.CharField()
        skills = serializers.CharField(max_length=1000)

    class OutputSerializer(serializers.Serializer):
        email = serializers.EmailField()
        first_name = serializers.CharField()
        last_name = serializers.CharField()
        bio = serializers.CharField(required=False)
        skills = serializers.CharField(required=False)

    def get(self, request):
        profile = Profile.objects.filter(user=request.user).first()
        data_response = {
            'email': profile.user.email,
            'first_name': profile.user.first_name,
            'last_name': profile.user.last_name,
            'bio': profile.bio,
            'skills': profile.skills,
        }
        output_serializer = self.OutputSerializer(data_response)
        return Response(
            data=output_serializer.data,
            status=status.HTTP_200_OK
        )

    def put(self, request):
        serializer_data = self.InputSerializer(data=request.data)
        serializer_data.is_valid(raise_exception=True)
        profile = Profile.objects.filter(user=request.user).first()
        profile.bio = serializer_data.validated_data['bio']
        profile.skills = serializer_data.validated_data['skills']
        profile.save()
        message_service = AdvMessagesService()
        message = message_service.create_message_system(profile)

        data_response = {
            'email': profile.user.email,
            'first_name': profile.user.first_name,
            'last_name': profile.user.last_name,
            'bio': profile.bio,
            'skills': profile.skills,
        }
        output_serializer = self.OutputSerializer(data_response)
        return Response(
            data=output_serializer.data,
            status=status.HTTP_200_OK
        )
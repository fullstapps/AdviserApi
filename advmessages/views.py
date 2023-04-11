from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework import permissions,serializers, exceptions, status
from django.conf import settings

from advmessages.services import AdvMessagesService
from .models import Profile, AdviserMessages
from rest_framework.response import Response
# Create your views here.

class MessageListView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    class OutputSerializer(serializers.Serializer):
        message = serializers.CharField()
        role = serializers.CharField()
        created_at = serializers.CharField()


    def get(self, request):
        profile = Profile.objects.filter(user=request.user).first()
        messages = AdviserMessages.objects.filter(profile=profile, role="assistant").order_by('id')
        output_serializer = self.OutputSerializer(data=messages, many=True)
        output_serializer.is_valid()

        return Response(
            data=output_serializer.data,
            status=status.HTTP_200_OK
        )



class RequestMessageView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    class OutputSerializer(serializers.Serializer):
        message = serializers.CharField()
        role = serializers.CharField()
        created_at = serializers.CharField()


    def get(self, request):
        profile = Profile.objects.filter(user=request.user).first()
        message_service = AdvMessagesService()
        message_user = message_service.create_message_user(profile)
        messages = message_service.get_messages(profile)
        response = message_service.set_messages_openai(messages)
        message_assistant = message_service.create_message_assistant(profile, response)
        output_serializer = self.OutputSerializer(message_assistant)

        return Response(
            data=output_serializer.data,
            status=status.HTTP_200_OK
        )


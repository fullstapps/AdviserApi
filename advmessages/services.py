
import os, openai
from django.conf import settings

from advmessages.models import AdviserMessages
from authentication.models import Profile


class AdvMessagesService:

    def __init__(self):
        openai.api_key = settings.OPENAI_KEY


    def create_message_system(self, profile: Profile):
        message_value = 'Eres una inteligencia artificial que ayuda a los desarrolladores a conseguir trabajo, mi perfil' \
                        ' es el siguiente: {} y mis skills son las siguientes: {}'.format(profile.bio, profile.skills)
        try:
            message = AdviserMessages.objects.get(profile=profile, role='system')
            message.message = message_value
            message.save()
        except:
            message = AdviserMessages(
                profile=profile,
                role='system',
                message=message_value
            )
            message.save()
        return message

    def create_message_user(self, profile: Profile):
        message_value = ''
        messages_count = AdviserMessages.objects.filter(profile=profile).count()
        if messages_count > 2:
            message_value = 'Me puedes dar otro  consejo diferente al anterior?'
        else:
            message_value = 'Me puedes dar un consejo para encontrar trabajo con mi perfil?'

        message = AdviserMessages(
            profile=profile,
            role='user',
            message=message_value
        )
        message.save()
        return message

    def get_messages(self, profile: Profile):
        messages = AdviserMessages.objects.filter(profile=profile).order_by('id')
        messages_data = []
        for message in messages:
            messages_data.append({
                "role": message.role,
                "content": message.message
            })
        return messages_data

    def create_message_assistant(self, profile: Profile, response):
        message_response = response['choices'][0]['message']['content']
        message = AdviserMessages(
            profile=profile,
            role='assistant',
            message=message_response,
            response=response
        )
        message.save()
        return message



    def set_messages_openai(self, messages):

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        return response
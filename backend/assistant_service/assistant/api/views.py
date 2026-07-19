from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from assistant.models import Client
from assistant.services.chat_storage import ChatStorageService
from assistant.services.rag_pipeline import RAGPipeline

class ChatView(APIView):
    def post(self, request):
        user_message = request.data.get('message')
        if not user_message:
            return Response({"error": "Empty message"}, status=status.HTTP_400_BAD_REQUEST)

        #ИДЕНТИФИКАЦИЯ (через Session)
        if not request.session.session_key:
            request.session.create()
        session_id = request.session.session_key
        
        #поиск клиента/создаем "теневой" профиль для этого чата
        client, created = Client.objects.get_or_create(
            session_id=session_id,
            defaults={'first_name': 'Гость'}
        )
        #БД И REDIS
        #достаем историю
        history = ChatStorageService.get_history(client)
        
        #сохраняем вопрос пользователя
        ChatStorageService.add_message(client, "user", user_message)

        #ответ
        pipeline = RAGPipeline()
        result = pipeline.generate_answer(user_message, history)
        
        assistant_reply = result["text"]
        suggested_chips = result["chips"]

        #сохраняем ответ ассистента
        ChatStorageService.add_message(client, "assistant", assistant_reply)

        return Response({
            "reply": assistant_reply,
            "suggested_chips": suggested_chips
        }, status=status.HTTP_200_OK)

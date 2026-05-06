from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from ..services.rag_pipeline import RAGPipeline

class ChatView(APIView):
    def post(self, request):
        user_message = request.data.get("message")
        
        if not user_message:
            return Response(
                {"error": "Поле 'message' обязательно для заполнения."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        #историю из сессии
        history = request.session.get('chat_history', [])

        #вызываем пайплайн
        pipeline = RAGPipeline()
        reply = pipeline.generate_answer(user_message, history)

        #обновляем историю диалога
        history.append({"role": "user", "text": user_message})
        history.append({"role": "assistant", "text": reply})
        request.session['chat_history'] = history[-10:]
        
        return Response({"reply": reply}, status=status.HTTP_200_OK)
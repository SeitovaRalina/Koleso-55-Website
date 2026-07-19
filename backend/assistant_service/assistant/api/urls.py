from django.urls import path
from django.views.generic import TemplateView
from .views import ChatView

urlpatterns = [
    path('v1/chat/', ChatView.as_view(), name='chat_api'),
    
    path('ui/', TemplateView.as_view(template_name='chat.html'), name='chat_ui'),
]


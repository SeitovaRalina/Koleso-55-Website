from django.core.cache import cache
from assistant.models import ChatMessage, Client

class ChatStorageService:
    CONTEXT_LIMIT = 10  
    CACHE_TTL = 3600   

    @classmethod
    def get_history(cls, client: Client) -> list:
        cache_key = f"chat_history_{client.id}"
        history = cache.get(cache_key)

        if history is None:
            db_messages = ChatMessage.objects.filter(client=client).order_by('-created_at')[:cls.CONTEXT_LIMIT]
            
            history = [{"role": msg.role, "text": msg.content} for msg in reversed(db_messages)]
            
            cache.set(cache_key, history, timeout=cls.CACHE_TTL)

        return history

    @classmethod
    def add_message(cls, client: Client, role: str, text: str):
        ChatMessage.objects.create(client=client, role=role, content=text)
        
        cache_key = f"chat_history_{client.id}"
        history = cache.get(cache_key)
        
        if history is not None:
            history.append({"role": role, "text": text})
            cache.set(cache_key, history[-cls.CONTEXT_LIMIT:], timeout=cls.CACHE_TTL)
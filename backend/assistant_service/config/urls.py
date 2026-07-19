from django.http import JsonResponse
from django.urls import include, path

urlpatterns = [
    path('health/', lambda request: JsonResponse({'status': 'ok'}), name='health'),
    # Включаем assistant API напрямую без префикса, так как в assistant.api.urls уже есть пути
    path('', include('assistant.api.urls')),
]

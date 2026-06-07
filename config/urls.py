from django.urls import path, include

urlpatterns = [
    # Включаем assistant API напрямую без префикса, так как в assistant.api.urls уже есть пути
    path('', include('assistant.api.urls')),
]

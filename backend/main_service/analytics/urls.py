from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    # Analytics endpoints
    path('view/start/', views.view_start, name='view_start'),
    path('view/heartbeat/', views.view_heartbeat, name='view_heartbeat'),
    path('view/end/', views.view_end, name='view_end'),
    
    # Internal API endpoints
    path('internal/excursions/', views.internal_excursions, name='internal_excursions'),
    path('internal/popularity/', views.internal_popularity, name='internal_popularity'),
]

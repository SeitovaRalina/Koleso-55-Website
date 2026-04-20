from django.urls import path
from .views import ExcursionListView, ExcursionDetailView

app_name = 'excursions'

urlpatterns = [
    path('', ExcursionListView.as_view(), name='excursion-list'),
    path('<slug:slug>/', ExcursionDetailView.as_view(), name='excursion-detail'),
]

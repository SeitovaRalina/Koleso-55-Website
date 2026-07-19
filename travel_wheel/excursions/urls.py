from django.urls import path
from .views import (
    ExcursionListView,
    ExcursionDetailView,
    CategoryListView
)

urlpatterns = [
    path("", ExcursionListView.as_view()),
    path("<int:pk>/", ExcursionDetailView.as_view()),
    path("categories/", CategoryListView.as_view()),
]

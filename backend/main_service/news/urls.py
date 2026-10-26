from django.urls import path

from .views import NewsCategoryListView, NewsDetailView, NewsListView

app_name = 'news'

urlpatterns = [
    path('', NewsListView.as_view(), name='list'),
    path('categories/', NewsCategoryListView.as_view(), name='categories'),
    path('<str:slug>/', NewsDetailView.as_view(), name='detail'),
]

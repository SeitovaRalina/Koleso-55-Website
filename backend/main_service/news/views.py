from django.utils import timezone
from rest_framework import generics, permissions

from .models import NewsArticle
from .serializers import NewsArticleSerializer


class PublishedNewsQuerysetMixin:
    serializer_class = NewsArticleSerializer
    permission_classes = (permissions.AllowAny,)

    def get_queryset(self):
        return NewsArticle.objects.filter(is_published=True, published_at__lte=timezone.now())


class NewsListView(PublishedNewsQuerysetMixin, generics.ListAPIView):
    pass


class NewsDetailView(PublishedNewsQuerysetMixin, generics.RetrieveAPIView):
    lookup_field = 'slug'

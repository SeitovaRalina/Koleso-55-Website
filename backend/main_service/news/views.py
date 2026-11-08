from django.utils import timezone
from rest_framework import generics, permissions

from .models import NewsArticle, NewsCategory
from .serializers import NewsArticleDetailSerializer, NewsArticleSerializer, NewsCategorySerializer


class PublishedNewsQuerysetMixin:
    serializer_class = NewsArticleSerializer
    permission_classes = (permissions.AllowAny,)

    def get_queryset(self):
        return NewsArticle.objects.select_related('category').filter(
            is_published=True, published_at__lte=timezone.now()
        )


class NewsListView(PublishedNewsQuerysetMixin, generics.ListAPIView):
    def get_queryset(self):
        queryset = super().get_queryset()
        category = self.request.query_params.get('category')
        return queryset.filter(category__slug=category) if category else queryset


class NewsDetailView(PublishedNewsQuerysetMixin, generics.RetrieveAPIView):
    serializer_class = NewsArticleDetailSerializer
    lookup_field = 'slug'

    def get_queryset(self):
        return super().get_queryset().prefetch_related('blocks')


class NewsCategoryListView(generics.ListAPIView):
    serializer_class = NewsCategorySerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = None

    def get_queryset(self):
        return NewsCategory.objects.filter(
            articles__is_published=True, articles__published_at__lte=timezone.now()
        ).distinct()

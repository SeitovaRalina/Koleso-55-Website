from rest_framework import generics, filters as drf_filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Excursion
from .serializers import ExcursionListSerializer, ExcursionDetailSerializer
from .filters import ExcursionFilter


class ExcursionListView(generics.ListAPIView):
    queryset = Excursion.objects.filter(is_active=True).prefetch_related('images')
    serializer_class = ExcursionListSerializer

    filter_backends = [
        DjangoFilterBackend,           # наши фильтры из filters.py
        drf_filters.SearchFilter,      # ?search=...
        drf_filters.OrderingFilter,    # ?ordering=price,-duration
    ]

    filterset_class = ExcursionFilter
    search_fields = ['title', 'short_description']
    ordering_fields = ['price', 'duration', 'created_at']
    ordering = ['-created_at']


class ExcursionDetailView(generics.RetrieveAPIView):
    queryset = Excursion.objects.filter(is_active=True).prefetch_related('images', 'slots')
    serializer_class = ExcursionDetailSerializer
    lookup_field = 'slug'

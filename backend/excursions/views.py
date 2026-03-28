from rest_framework import generics
from .models import Excursion
from .serializers import ExcursionListSerializer, ExcursionDetailSerializer


class ExcursionListView(generics.ListAPIView):
    queryset = Excursion.objects.filter(is_active=True).prefetch_related('images')
    serializer_class = ExcursionListSerializer


class ExcursionDetailView(generics.RetrieveAPIView):
    queryset = Excursion.objects.filter(is_active=True).prefetch_related('images', 'slots')
    serializer_class = ExcursionDetailSerializer
    lookup_field = 'slug'
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import Excursion, Category
from .serializers import (
    ExcursionListSerializer,
    ExcursionDetailSerializer,
    CategorySerializer
)


class ExcursionListView(ListAPIView):
    queryset = Excursion.objects.select_related("category")
    serializer_class = ExcursionListSerializer
    permission_classes = [AllowAny]

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["category"]
    search_fields = ["title", "description"]
    ordering_fields = ["price", "created_at"]


class ExcursionDetailView(RetrieveAPIView):
    queryset = Excursion.objects.prefetch_related("slots", "category")
    serializer_class = ExcursionDetailSerializer
    permission_classes = [AllowAny]


class CategoryListView(ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
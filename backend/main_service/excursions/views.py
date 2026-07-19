from rest_framework import generics, filters as drf_filters
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from drf_spectacular.utils import OpenApiExample, extend_schema

from .filters import ExcursionFilter
from .models import Excursion, Category
from .serializers import ExcursionDetailSerializer, ExcursionListSerializer, CategorySerializer


@extend_schema(
    summary="Список экскурсий",
    description="Возвращает список активных экскурсий с основной информацией, рейтингом и изображениями.",
    examples=[
        OpenApiExample(
            "Excursion list response",
            response_only=True,
            value={
                "count": 1,
                "next": None,
                "previous": None,
                "results": [
                    {
                        "id": 1,
                        "title": "Omsk city highlights",
                        "slug": "obzornaya-ekskursiya-po-omsku",
                        "short_description": "A short city tour with the main landmarks.",
                        "location_type_display": "City excursions",
                        "price": "1500.00",
                        "duration": 120,
                        "category": {"id": 1, "name": "City", "slug": "gorodskie"},
                        "main_image": "http://example.com/media/excursions/2024/01/15/photo.jpg",
                        "average_rating": 4.5,
                        "review_count": 23,
                    }
                ],
            },
        )
    ],
)
class ExcursionListView(generics.ListAPIView):
    queryset = Excursion.objects.filter(is_active=True).prefetch_related("images", "reviews")
    serializer_class = ExcursionListSerializer

    filter_backends = [
        DjangoFilterBackend,
        drf_filters.SearchFilter,
        drf_filters.OrderingFilter,
    ]

    filterset_class = ExcursionFilter
    search_fields = ["title", "short_description"]
    ordering_fields = ["price", "duration", "created_at"]
    ordering = ["-created_at"]

    def list(self, request, *args, **kwargs):
        if request.query_params.getlist("ids"):
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)

        return super().list(request, *args, **kwargs)


@extend_schema(
    summary="Детальная информация об экскурсии",
    description="Возвращает полную информацию об экскурсии, включая изображения, слоты и отзывы.",
    examples=[
        OpenApiExample(
            "Excursion detail response",
            response_only=True,
            value={
                "id": 1,
                "title": "Omsk city highlights",
                "slug": "obzornaya-ekskursiya-po-omsku",
                "description": "A detailed sightseeing program around the city center.",
                "short_description": "A short city tour with the main landmarks.",
                "price": "1500.00",
                "duration": 120,
                "category": {"id": 1, "name": "City", "slug": "gorodskie"},
                "location_type_display": "City excursions",
                "images": [
                    {
                        "id": 1,
                        "image": "http://example.com/media/photo1.jpg",
                        "alt_text": "Photo 1",
                        "is_main": True,
                    }
                ],
                "slots": [
                    {
                        "id": 1,
                        "date": "2024-12-25",
                        "time": "10:00",
                        "max_participants": 20,
                        "available_seats": 15,
                        "is_available": True,
                    }
                ],
                "is_active": True,
                "approved_reviews": [],
                "average_rating": 4.5,
                "review_count": 23,
            },
        )
    ],
)
class ExcursionDetailView(generics.RetrieveAPIView):
    queryset = Excursion.objects.filter(is_active=True).prefetch_related("images", "slots")
    serializer_class = ExcursionDetailSerializer
    lookup_field = "pk"


@extend_schema(
    summary="Список категорий",
    description="Возвращает список всех категорий экскурсий.",
)
class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


@extend_schema(
    summary="Максимальная цена",
    description="Возвращает максимальную цену среди всех экскурсий.",
)
class MaxPriceView(generics.ListAPIView):
    queryset = Excursion.objects.all()
    serializer_class = ExcursionListSerializer

    def list(self, request, *args, **kwargs):
        from django.db.models import Max
        max_price = self.queryset.aggregate(max_price=Max('price'))['max_price'] or 10000
        from rest_framework.response import Response
        return Response({'max_price': max_price})

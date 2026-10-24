from rest_framework import generics, filters as drf_filters, permissions, status
from rest_framework.response import Response
from rest_framework.throttling import SimpleRateThrottle
from rest_framework.views import APIView
from django.db import IntegrityError, transaction
from django_filters.rest_framework import DjangoFilterBackend

from drf_spectacular.utils import OpenApiExample, extend_schema

from .filters import ExcursionFilter
from .models import Excursion, Category, ExcursionInquiry
from .serializers import ExcursionDetailSerializer, ExcursionListSerializer, CategorySerializer, ExcursionInquirySerializer


class InquiryThrottle(SimpleRateThrottle):
    rate = '5/hour'

    def get_cache_key(self, request, view):
        return self.cache_format % {'scope': 'inquiry', 'ident': self.get_ident(request)}


@extend_schema(
    summary='Отправить вопрос по программе',
    description='Гостевая отправка. Повтор с тем же request_id и теми же данными возвращает тот же результат. Данные доступны только в Django Admin.',
    request=ExcursionInquirySerializer,
    responses={201: None, 400: None, 429: None},
)
class ExcursionInquiryCreateView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [InquiryThrottle]

    def post(self, request):
        serializer = ExcursionInquirySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        existing = ExcursionInquiry.objects.filter(request_id=data['request_id']).first()
        if existing:
            if all(getattr(existing, key) == value for key, value in data.items()):
                return Response({'id': existing.id}, status=status.HTTP_201_CREATED)
            return Response({'request_id': ['Ключ уже использован для другого обращения.']}, status=status.HTTP_400_BAD_REQUEST)
        try:
            with transaction.atomic():
                inquiry = ExcursionInquiry.objects.create(**data)
        except IntegrityError:
            existing = ExcursionInquiry.objects.get(request_id=data['request_id'])
            if not all(getattr(existing, key) == value for key, value in data.items()):
                return Response({'request_id': ['Ключ уже использован для другого обращения.']}, status=status.HTTP_400_BAD_REQUEST)
            inquiry = existing
        return Response({'id': inquiry.id}, status=status.HTTP_201_CREATED)


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

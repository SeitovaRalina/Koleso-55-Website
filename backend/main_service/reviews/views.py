from rest_framework import generics, permissions, filters as drf_filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db import models

from .models import Review, ReviewStatus
from .serializers import ReviewCreateSerializer, ReviewListSerializer, ReviewUpdateSerializer
from drf_spectacular.utils import extend_schema
from analytics.services import publish_recommendation_event

@extend_schema(
    summary="Создание отзыва на экскурсию",
    description="Позволяет авторизованному пользователю создать новый отзыв на экскурсию. "
                "Отзыв будет находиться в статусе 'pending' до проверки модератором.",
)
class ReviewCreateView(generics.CreateAPIView):
    serializer_class = ReviewCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        review = serializer.save(user=self.request.user)
        publish_recommendation_event(
            event_type="review",
            user_id=self.request.user.id,
            excursion_id=review.excursion_id,
            source="direct",
        )

@extend_schema(
    summary="Список отзывов на экскурсию",
    description="Возвращает список одобренных отзывов на экскурсию с возможностью сортировки",
)
class ReviewListView(generics.ListAPIView):
    serializer_class = ReviewListSerializer
    filter_backends = [drf_filters.OrderingFilter]
    ordering_fields = ['created_at', 'rating']
    ordering = ['-created_at']  # По умолчанию - новые первые

    def get_queryset(self):
        excursion_id = self.kwargs['excursion_id']
        sort_param = self.request.query_params.get('sort', 'time')
        
        queryset = Review.objects.filter(
            excursion_id=excursion_id,
            status='approved'
        ).select_related('user').prefetch_related('images')
        
        # Сортировка по параметрам
        if sort_param == 'photos':
            # Сначала отзывы с фото, потом без
            queryset = queryset.annotate(
                has_photos=models.Count('images')
            ).order_by('-has_photos', '-created_at')
        elif sort_param == 'rating':
            # По убыванию рейтинга
            queryset = queryset.order_by('-rating', '-created_at')
        else:  # time (по умолчанию)
            # По времени (новые первые)
            queryset = queryset.order_by('-created_at')
            
        return queryset

@extend_schema(
    summary="Редактирование отзыва",
    description="Позволяет автору отзыва редактировать его, если отзыв находится в статусе 'pending'. "
                "После редактирования отзыв снова будет отправлен на проверку модератором.",
)
class ReviewUpdateView(generics.UpdateAPIView):
    serializer_class = ReviewUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Review.objects.filter(user=self.request.user, status=ReviewStatus.PENDING)

@extend_schema(
    summary="Список отзывов текущего пользователя",
    description="Возвращает список всех отзывов, оставленных текущим пользователем, с их статусами.",
)
class MyReviewsListView(generics.ListAPIView):
    serializer_class = ReviewListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Review.objects.filter(user=self.request.user).select_related('excursion').order_by('-created_at')

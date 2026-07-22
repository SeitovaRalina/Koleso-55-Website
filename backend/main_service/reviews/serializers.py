from typing import List, Optional, Dict, Any
from decimal import Decimal

from rest_framework import serializers
from drf_spectacular.utils import extend_schema, extend_schema_field
from drf_spectacular.types import OpenApiTypes
from .models import Review, ReviewImage, ReviewStatus
from .services.profanity_filter import toxicity_filter
from excursions.models import Excursion


class ReviewImageSerializer(serializers.ModelSerializer):
    """Сериализатор изображений к отзывам"""
    
    id = serializers.IntegerField(
        label="ID",
        help_text="Уникальный идентификатор изображения",
        read_only=True
    )
    image = serializers.ImageField(
        label="Изображение",
        help_text="Фотография к отзыву"
    )
    
    class Meta:
        model = ReviewImage
        fields = ['id', 'image']


class ReviewCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания отзыва"""
    
    excursion = serializers.IntegerField(
        label="Экскурсия",
        help_text="ID экскурсии, на которую оставляется отзыв"
    )
    rating = serializers.IntegerField(
        label="Оценка",
        help_text="Оценка экскурсии от 1 до 5 звезд",
        min_value=1,
        max_value=5
    )
    text = serializers.CharField(
        label="Текст отзыва",
        help_text="Текст отзыва (максимум 2000 символов)",
        max_length=2000,
        required=True
    )
    images = ReviewImageSerializer(
        label="Изображения",
        help_text="Фотографии к отзыву (необязательно)",
        many=True,
        required=False
    )

    class Meta:
        model = Review
        fields = ['excursion', 'rating', 'text', 'images']

    def validate(self, attrs):
        request = self.context['request']
        excursion_id = attrs['excursion']
        try:
            excursion = Excursion.objects.get(id=excursion_id, is_active=True)
        except Excursion.DoesNotExist:
            raise serializers.ValidationError({"excursion": "Экскурсия не найдена или неактивна"})

        has_completed_order = request.user.orders.filter(
            excursion=excursion,
            status='completed'
        ).exists()

        if not has_completed_order:
            raise serializers.ValidationError(
                "Оставить отзыв можно только после посещения экскурсии (статус заказа «Выполнен»)."
            )

        check = toxicity_filter.is_toxic(attrs['text'])

        attrs['is_toxic'] = check['is_toxic']
        attrs['toxicity_score'] = check['score']

        if check['is_toxic']:
            attrs['status'] = ReviewStatus.REJECTED
        else:
            attrs['status'] = ReviewStatus.PENDING

        attrs['excursion'] = excursion

        return attrs


class ReviewListSerializer(serializers.ModelSerializer):
    """Сериализатор списка отзывов"""
    
    id = serializers.IntegerField(
        label="ID",
        help_text="Уникальный идентификатор отзыва",
        read_only=True
    )
    user_name = serializers.CharField(
        label="Имя пользователя",
        help_text="Полное имя пользователя, оставившего отзыв",
        source='user.get_full_name',
        read_only=True
    )
    rating = serializers.IntegerField(
        label="Оценка",
        help_text="Оценка экскурсии от 1 до 5 звезд",
        read_only=True
    )
    text = serializers.CharField(
        label="Текст отзыва",
        help_text="Текст отзыва",
        read_only=True
    )
    images = ReviewImageSerializer(
        label="Изображения",
        help_text="Фотографии к отзыву",
        many=True,
        read_only=True
    )
    created_at = serializers.DateTimeField(
        label="Дата создания",
        help_text="Дата и время создания отзыва",
        read_only=True
    )

    class Meta:
        model = Review
        fields = ['id', 'user_name', 'rating', 'text', 'images', 'created_at']


class HomepageReviewSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()
    main_photo = serializers.SerializerMethodField()
    excursion_id = serializers.IntegerField(source='excursion.id', read_only=True)
    excursion_title = serializers.CharField(source='excursion.title', read_only=True)

    class Meta:
        model = Review
        fields = [
            'id',
            'author_name',
            'rating',
            'text',
            'main_photo',
            'excursion_id',
            'excursion_title',
            'created_at',
        ]

    def get_author_name(self, obj: Review) -> str:
        return obj.homepage_author_name or obj.user.get_full_name() or obj.user.email

    def get_main_photo(self, obj: Review) -> Optional[str]:
        selected_image = obj.images.filter(is_homepage_main=True).order_by('homepage_order', 'uploaded_at').first()
        if selected_image:
            return selected_image.image.url

        first_image = obj.images.order_by('homepage_order', 'uploaded_at').first()
        if first_image:
            return first_image.image.url

        if obj.homepage_main_photo:
            return obj.homepage_main_photo.url

        return None


class ReviewUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для редактирования отзыва"""
    
    rating = serializers.IntegerField(
        label="Оценка",
        help_text="Оценка экскурсии от 1 до 5 звезд",
        min_value=1,
        max_value=5,
        required=False
    )
    text = serializers.CharField(
        label="Текст отзыва",
        help_text="Текст отзыва (максимум 2000 символов)",
        max_length=2000,
        required=False,
        allow_blank=True
    )
    images = ReviewImageSerializer(
        label="Изображения",
        help_text="Фотографии к отзыву (необязательно)",
        many=True,
        required=False
    )
    
    class Meta:
        model = Review
        fields = ['rating', 'text', 'images']

    def validate(self, attrs):
        if self.instance and not self.instance.can_be_edited():
            raise serializers.ValidationError(
                "Редактировать можно только отзывы, находящиеся на модерации."
            )
        return attrs

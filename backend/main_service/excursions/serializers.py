from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from .models import Excursion, Category, ExcursionImage, Slot
from reviews.serializers import ReviewListSerializer


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']


class ExcursionImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExcursionImage
        fields = ['id', 'image', 'alt_text', 'is_main']


class SlotSerializer(serializers.ModelSerializer):
    available_seats = serializers.IntegerField(read_only=True)
    is_available = serializers.BooleanField(read_only=True)

    class Meta:
        model = Slot
        fields = [
            'id', 'date', 'time', 'max_participants',
            'available_seats', 'is_available', 'price_override'
        ]


class ExcursionListSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    main_image = serializers.SerializerMethodField()
    location_type_display = serializers .CharField(source='get_location_type_display', read_only=True)

    average_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()

    class Meta:
        model = Excursion
        fields = [
            'id', 'title', 'slug', 'short_description',
            'location_type_display', 'price', 'duration', 'category', 'main_image',
            'average_rating', 'review_count'
        ]

    @extend_schema_field(serializers.URLField())
    def get_main_image(self, obj):
        main = obj.images.filter(is_main=True).first()
        return main.image.url if main else None

    @extend_schema_field(serializers.FloatField(allow_null=True))
    def get_average_rating(self, obj):
        """Средний рейтинг только по одобренным отзывам"""
        from django.db.models import Avg
        avg = obj.reviews.filter(status='approved').aggregate(Avg('rating'))['rating__avg']
        return round(avg, 1) if avg is not None else None

    @extend_schema_field(serializers.IntegerField())
    def get_review_count(self, obj):
        """Количество одобренных отзывов"""
        return obj.reviews.filter(status='approved').count()


class ExcursionDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    images = ExcursionImageSerializer(many=True, read_only=True)
    slots = SlotSerializer(many=True, read_only=True)
    location_type_display = serializers.CharField(source='get_location_type_display', read_only=True)

    approved_reviews = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()

    class Meta:
        model = Excursion
        fields = [
            'id', 'title', 'slug', 'description', 'short_description',
            'price', 'duration', 'category', 'location_type_display', 'images', 'slots', 'is_active',
            'approved_reviews', 'average_rating', 'review_count'
        ]

    @extend_schema_field(ReviewListSerializer(many=True))
    def get_approved_reviews(self, obj):
        """Только одобренные отзывы, отсортированные по новизне"""
        reviews = obj.reviews.filter(status='approved').order_by('-created_at')[:10]
        return ReviewListSerializer(reviews, many=True).data

    def get_average_rating(self, obj):
        """Средний рейтинг экскурсии"""
        from django.db.models import Avg
        avg = obj.reviews.filter(status='approved').aggregate(Avg('rating'))['rating__avg']
        return round(avg, 1) if avg else None

    def get_review_count(self, obj):
        """Количество одобренных отзывов"""
        return obj.reviews.filter(status='approved').count()

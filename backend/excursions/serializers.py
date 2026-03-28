from rest_framework import serializers
from .models import Excursion, Category, ExcursionImage, Slot


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']


class ExcursionImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExcursionImage
        fields = ['id', 'image', 'alt_text', 'is_main']


class SlotSerializer(serializers.ModelSerializer):
    available_seats = serializers.ReadOnlyField()
    is_available = serializers.ReadOnlyField()

    class Meta:
        model = Slot
        fields = [
            'id', 'date', 'time', 'max_participants',
            'available_seats', 'is_available', 'price_override'
        ]


class ExcursionListSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    main_image = serializers.SerializerMethodField()

    class Meta:
        model = Excursion
        fields = [
            'id', 'title', 'slug', 'short_description',
            'price', 'duration', 'category', 'main_image'
        ]

    def get_main_image(self, obj):
        main = obj.images.filter(is_main=True).first()
        return main.image.url if main else None


class ExcursionDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    images = ExcursionImageSerializer(many=True, read_only=True)
    slots = SlotSerializer(many=True, read_only=True)

    class Meta:
        model = Excursion
        fields = [
            'id', 'title', 'slug', 'description', 'short_description',
            'price', 'duration', 'category', 'images', 'slots', 'is_active'
        ]

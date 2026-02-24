from rest_framework import serializers
from .models import Category, Excursion, ExcursionSlot

class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = [
            "id",
            "vk_id",
            "title",
            "image"
        ]
        read_only_fields = fields

class ExcursionSlotSerializer(serializers.ModelSerializer):

    available_places = serializers.SerializerMethodField()

    class Meta:
        model = ExcursionSlot
        fields = [
            "id",
            "date",
            "total_places",
            "booked_places",
            "available_places"
        ]
        read_only_fields = fields

    def get_available_places(self, obj):
        return obj.total_places - obj.booked_places

class ExcursionListSerializer(serializers.ModelSerializer):

    category = CategorySerializer()

    class Meta:
        model = Excursion
        fields = [
            "id",
            "title",
            "price",
            "duration",
            "image",
            "category"
        ]
        read_only_fields = fields

class ExcursionDetailSerializer(serializers.ModelSerializer):

    category = CategorySerializer()
    slots = ExcursionSlotSerializer(many=True)

    class Meta:
        model = Excursion
        fields = [
            "id",
            "title",
            "description",
            "price",
            "duration",
            "image",
            "category",
            "slots"
        ]
        read_only_fields = fields

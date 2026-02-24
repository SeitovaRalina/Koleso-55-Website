from rest_framework import serializers
from .models import Cart, CartItem
from excursions.models import Excursion

class CartItemSerializer(serializers.ModelSerializer):

    excursion_title = serializers.CharField(source="excursion.title", read_only=True)
    price = serializers.DecimalField(
        source="excursion.price",
        max_digits=10,
        decimal_places=2,
        read_only=True
    )

    class Meta:
        model = CartItem
        fields = [
            "id",
            "excursion",
            "excursion_title",
            "persons",
            "price"
        ]

class CartSerializer(serializers.ModelSerializer):

    items = CartItemSerializer(many=True)

    class Meta:
        model = Cart
        fields = ["id", "items"]

class AddToCartSerializer(serializers.Serializer):

    excursion_id = serializers.IntegerField()
    persons = serializers.IntegerField(min_value=1)

    def validate_excursion_id(self, value):
        if not Excursion.objects.filter(id=value).exists():
            raise serializers.ValidationError("Экскурсия не найдена")
        return value

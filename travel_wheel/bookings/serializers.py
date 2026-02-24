from rest_framework import serializers
from django.db import transaction
from .models import Booking
from excursions.models import ExcursionSlot

class BookingListSerializer(serializers.ModelSerializer):

    excursion_title = serializers.CharField(source="excursion.title", read_only=True)
    date = serializers.DateField(source="slot.date", read_only=True)

    class Meta:
        model = Booking
        fields = [
            "id",
            "excursion_title",
            "date",
            "persons",
            "total_price",
            "status",
            "created_at"
        ]
        read_only_fields = fields

class BookingDetailSerializer(serializers.ModelSerializer):

    excursion = serializers.StringRelatedField()
    date = serializers.DateField(source="slot.date")

    class Meta:
        model = Booking
        fields = "__all__"
        read_only_fields = [
            "user",
            "total_price",
            "status",
            "created_at"
        ]

class CreateBookingSerializer(serializers.Serializer):

    slot_id = serializers.IntegerField()
    persons = serializers.IntegerField(min_value=1)

    def validate(self, attrs):

        try:
            slot = ExcursionSlot.objects.select_for_update().get(
                id=attrs["slot_id"]
            )
        except ExcursionSlot.DoesNotExist:
            raise serializers.ValidationError("Слот не найден")

        if slot.total_places - slot.booked_places < attrs["persons"]:
            raise serializers.ValidationError("Недостаточно свободных мест")

        attrs["slot"] = slot
        return attrs

    @transaction.atomic
    def create(self, validated_data):

        user = self.context["request"].user
        slot = validated_data["slot"]
        persons = validated_data["persons"]

        slot.booked_places += persons
        slot.save()

        total_price = slot.excursion.price * persons

        booking = Booking.objects.create(
            user=user,
            excursion=slot.excursion,
            slot=slot,
            persons=persons,
            total_price=total_price
        )

        return booking

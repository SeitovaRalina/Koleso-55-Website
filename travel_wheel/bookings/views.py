from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction

from .models import Booking
from .serializers import (
    BookingListSerializer,
    BookingDetailSerializer,
    CreateBookingSerializer
)


class BookingListView(ListAPIView):
    serializer_class = BookingListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)


class BookingDetailView(RetrieveAPIView):
    serializer_class = BookingDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)


class CreateBookingView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CreateBookingSerializer(
            data=request.data,
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        booking = serializer.save()
        return Response({"id": booking.id})


class CancelBookingView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, pk):

        booking = get_object_or_404(
            Booking.objects.select_for_update(),
            pk=pk,
            user=request.user
        )

        if booking.status == "cancelled":
            return Response({"error": "Уже отменено"}, status=400)

        booking.slot.booked_places -= booking.persons
        booking.slot.save()

        booking.status = "cancelled"
        booking.save()

        return Response({"status": "cancelled"})
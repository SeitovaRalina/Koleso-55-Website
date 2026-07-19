from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Cart, CartItem
from .serializers import CartSerializer, AddToCartSerializer
from bookings.models import Booking


class CartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)


class AddToCartView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):

        serializer = AddToCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        cart, _ = Cart.objects.get_or_create(user=request.user)

        CartItem.objects.create(
            cart=cart,
            excursion_id=serializer.validated_data["excursion_id"],
            persons=serializer.validated_data["persons"]
        )

        return Response({"status": "added"})


class RemoveFromCartView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):

        cart = get_object_or_404(Cart, user=request.user)
        item = get_object_or_404(CartItem, pk=pk, cart=cart)
        item.delete()

        return Response({"status": "removed"})


class CheckoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):

        cart = get_object_or_404(Cart, user=request.user)

        for item in cart.items.all():
            Booking.objects.create(
                user=request.user,
                excursion=item.excursion,
                slot=item.excursion.slots.first(),
                persons=item.persons,
                total_price=item.excursion.price * item.persons
            )

        cart.items.all().delete()

        return Response({"status": "checkout_complete"})
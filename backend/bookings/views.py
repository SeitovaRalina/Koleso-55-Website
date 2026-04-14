from rest_framework import generics, permissions

from .serializers import TourOrderCreateSerializer

class TourOrderCreateView(generics.CreateAPIView):
    serializer_class = TourOrderCreateSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        serializer.save()

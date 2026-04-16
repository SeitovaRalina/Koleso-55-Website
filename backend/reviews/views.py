from rest_framework import generics, permissions

from .models import Review
from .serializers import ReviewCreateSerializer, ReviewListSerializer

class ReviewCreateView(generics.CreateAPIView):
    serializer_class = ReviewCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, status='pending')

class ReviewListView(generics.ListAPIView):
    serializer_class = ReviewListSerializer

    def get_queryset(self):
        excursion_id = self.kwargs['excursion_id']
        return Review.objects.filter(
            excursion_id=excursion_id,
            status='approved'
        ).select_related('user')

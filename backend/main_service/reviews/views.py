from rest_framework import generics, permissions

from .models import Review, ReviewStatus
from .serializers import ReviewCreateSerializer, ReviewListSerializer, ReviewUpdateSerializer

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

class ReviewUpdateView(generics.UpdateAPIView):
    serializer_class = ReviewUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Review.objects.filter(user=self.request.user, status=ReviewStatus.PENDING)

class MyReviewsListView(generics.ListAPIView):
    serializer_class = ReviewListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Review.objects.filter(user=self.request.user).select_related('excursion').order_by('-created_at')

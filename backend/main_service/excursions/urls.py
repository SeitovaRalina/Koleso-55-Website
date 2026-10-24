from django.urls import path
from .views import ExcursionListView, ExcursionDetailView, CategoryListView, MaxPriceView, ExcursionInquiryCreateView

app_name = 'excursions'

urlpatterns = [
    path('inquiries/', ExcursionInquiryCreateView.as_view(), name='inquiry-create'),
    path('', ExcursionListView.as_view(), name='excursion-list'),
    path('<int:pk>/', ExcursionDetailView.as_view(), name='excursion-detail'),
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('max-price/', MaxPriceView.as_view(), name='max-price'),
]

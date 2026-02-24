from django.urls import path
from .views import (
    CartView,
    AddToCartView,
    RemoveFromCartView,
    CheckoutView
)

urlpatterns = [
    path("", CartView.as_view()),
    path("add/", AddToCartView.as_view()),
    path("remove/<int:pk>/", RemoveFromCartView.as_view()),
    path("checkout/", CheckoutView.as_view()),
]

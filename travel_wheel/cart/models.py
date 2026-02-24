from django.conf import settings
from django.db import models


class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    excursion = models.ForeignKey("excursions.Excursion", on_delete=models.CASCADE)
    persons = models.PositiveIntegerField(default=1)
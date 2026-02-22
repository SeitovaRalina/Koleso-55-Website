from django.db import models

# Create your models here.
class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    excursion = models.ForeignKey(Excursion, on_delete=models.CASCADE)
    people_count = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
from django.db import models

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=255)

class Excursion(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.IntegerField()  # в часах
    created_at = models.DateTimeField(auto_now_add=True)

class Review(models.Model):
    excursion = models.ForeignKey(Excursion, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
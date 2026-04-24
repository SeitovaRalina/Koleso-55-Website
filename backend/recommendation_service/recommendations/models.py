from django.db import models


class User(models.Model):
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(max_length=254, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'excursions_user'
        app_label = 'excursions'

    def __str__(self):
        return self.username


class Excursion(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    short_description = models.CharField(max_length=500)
    location = models.CharField(max_length=200)
    duration = models.IntegerField(help_text='Duration in minutes')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'excursions_excursion'
        app_label = 'excursions'

    def __str__(self):
        return self.title


class UserExcursion(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='excursions')
    excursion = models.ForeignKey(Excursion, on_delete=models.CASCADE, related_name='visitors')
    visited_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'excursions_userexcursion'
        unique_together = ['user', 'excursion']
        app_label = 'excursions'

    def __str__(self):
        return f"{self.user.username} - {self.excursion.title}"

import uuid
from django.db import models

class DialogCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    description = models.TextField(verbose_name='Описание категории диалога')

    def __str__(self):
        return self.description[:50]

class ExcursionCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    description = models.TextField(verbose_name='Описание категории экскурсии')

    def __str__(self):
        return self.description[:50]

class Client(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    external_id = models.CharField(max_length=255, unique=True, null=True, blank=True, verbose_name='Внешний ID (TG/Session)')
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    patronymic = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)

    def __str__(self):
        return f"{self.first_name or 'Гость'} {self.phone or ''}".strip()

class Excursion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    price_from = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.IntegerField(verbose_name='Длительность (мин)', null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    image_url = models.URLField(null=True, blank=True)
    category = models.ForeignKey(ExcursionCategory, on_delete=models.SET_NULL, null=True, related_name='excursions')
    is_active = models.BooleanField(default=True, verbose_name='Активна')

    def __str__(self):
        return self.title

class ChatMessage(models.Model):
    ROLE_CHOICES = (
        ('user', 'User'),
        ('assistant', 'Assistant'),
        ('system', 'System'),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.role}: {self.content[:10]}..."

class ChatState(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='states')
    category = models.ForeignKey(DialogCategory, on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateField(null=True, blank=True)
    budget = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    people_count = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"State for {self.client} at {self.created_at.strftime('%Y-%m-%d %H:%M')}"

class LeadRequest(models.Model):
    STATUS_CHOICES = (
        ('new', 'New'),
        ('processing', 'Processing'),
        ('closed', 'Closed'),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    excursion = models.ForeignKey(Excursion, on_delete=models.CASCADE, related_name='leads')
    chat_state = models.ForeignKey(ChatState, on_delete=models.CASCADE, related_name='leads')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    extra_notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Lead: {self.excursion.title} ({self.status})"
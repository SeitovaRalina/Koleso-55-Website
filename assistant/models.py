import uuid
from django.db import models

class DialogCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    description = models.TextField(verbose_name='Описание категории')

class ExcursionCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    description = models.TextField(verbose_name='Описание категории экскурсии')

class Client(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    patronymic = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)

class Excursion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    price_from = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.IntegerField(verbose_name='Длительность (мин)', null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    image_url = models.URLField(null=True, blank=True)
    category = models.ForeignKey(ExcursionCategory, on_delete=models.SET_NULL, null=True)
    is_active = models.BooleanField(default=True)

class ChatMessage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=15, default='user') # 'user' или 'assistant'
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

class ChatState(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.OneToOneField(Client, on_delete=models.CASCADE, related_name='chat_state')
    category = models.ForeignKey(DialogCategory, on_delete=models.SET_NULL, null=True)
    date = models.DateField(null=True, blank=True)
    budget = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    people_count = models.IntegerField(null=True, blank=True)

class LeadRequest(models.Model):
    STATUS_CHOICES = (('new', 'New'), ('processing', 'Processing'), ('closed', 'Closed'))
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    excursion = models.ForeignKey(Excursion, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    timestamp = models.DateTimeField(auto_now_add=True)
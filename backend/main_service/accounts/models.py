from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _
from .validators import normalize_phone


class CustomUserManager(BaseUserManager):

    def create_user(self, email, password=None, phone=None, **extra_fields):
        if not email:
            raise ValueError(_('Email обязателен'))
        
        email = self.normalize_email(email)
        phone = normalize_phone(phone) if phone else None
        
        user = self.model(
            email=email,
            phone=phone,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    username = None  # Удаляем поле username
    email = models.EmailField(
        _('Электронная почта'), 
        unique=True, 
        null=False,
        blank=False,
    )
    phone = models.CharField(
        _('Номер телефона'), 
        max_length=20, 
        unique=True, 
        null=True, 
        blank=True,
        help_text=_('Формат: +7XXXXXXXXXX')
    )
    is_email_verified = models.BooleanField(
        _('Email подтвержден'),
        default=False,
        help_text=_('Проверено ли подтверждение email')
    )
    
    # Поля имени оставляем опциональными, будут заполняться при бронировании
    first_name = models.CharField(
        _('Имя'), 
        max_length=150,
        blank=True,
    )
    last_name = models.CharField(
        _('Фамилия'), 
        max_length=150,
        blank=True,
    )
    patronymic = models.CharField(
        _('Отчество'), 
        max_length=150,
        blank=True,
    )

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.email

    def get_full_name(self):
        return f"{self.last_name} {self.first_name} {self.patronymic}".strip()

    def get_short_name(self):
        return self.first_name

    def save(self, *args, **kwargs):
        # Нормализуем телефон перед сохранением
        if self.phone:
            self.phone = normalize_phone(self.phone)
        super().save(*args, **kwargs)

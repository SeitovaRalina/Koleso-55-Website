from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from .validators import normalize_phone

User = get_user_model()


class CustomRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['email', 'phone', 'password', 'password2']
        extra_kwargs = {
            'email': {'required': True},
        }

    def validate_email(self, value):
        """Проверка уникальности email"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Пользователь с таким email уже существует")
        return value

    def validate_phone(self, value):
        """Валидация и нормализация телефона"""
        if value:
            normalized = normalize_phone(value)
            if not normalized:
                raise serializers.ValidationError("Неверный формат телефона. Используйте формат 8XXXXXXXXXX, +7XXXXXXXXXX или 9XXXXXXXXX")

            if User.objects.filter(phone=normalized).exists():
                raise serializers.ValidationError("Пользователь с таким телефоном уже существует")

            return normalized
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Пароли не совпадают"})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        
        # TODO: Отправка приветственного письма с ссылкой подтверждения email
        # Это можно реализовать асинхронно через Celery
        
        return user


class LoginSerializer(serializers.Serializer):
    contact = serializers.CharField(required=True)
    contact_type = serializers.ChoiceField(choices=['email', 'phone'], required=False)
    password = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        contact = attrs.get('contact')
        contact_type = attrs.get('contact_type')
        password = attrs.get('password')

        if not contact_type:
            contact_type = 'email' if '@' in contact else 'phone'

        if contact_type == 'email':
            # Поиск по email
            try:
                user = User.objects.get(email=contact)
            except User.DoesNotExist:
                raise serializers.ValidationError("Аккаунт с таким email не найден. Попробуйте войти по телефону.")
        else:
            # Нормализуем телефон и ищем
            normalized_phone = normalize_phone(contact)
            if not normalized_phone:
                raise serializers.ValidationError("Неверный формат телефона")

            try:
                user = User.objects.get(phone=normalized_phone)
            except User.DoesNotExist:
                raise serializers.ValidationError("Аккаунт с таким телефоном не найден. Попробуйте войти по email.")

        # Проверяем пароль
        if not user.check_password(password):
            raise serializers.ValidationError("Неверный пароль")

        if not user.is_active:
            raise serializers.ValidationError("Аккаунт неактивен")

        attrs['user'] = user
        return attrs

    def create(self, validated_data):
        user = validated_data['user']

        # Генерируем JWT токены
        refresh = RefreshToken.for_user(user)

        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'id': user.id,
                'email': user.email,
                'phone': user.phone,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'patronymic': user.patronymic,
                'is_email_verified': user.is_email_verified,
            },
            'message': 'Email не подтвержден' if not user.is_email_verified else None
        }


class PasswordResetSerializer(serializers.Serializer):
    contact = serializers.CharField(required=True)
    contact_type = serializers.ChoiceField(choices=['email', 'phone'], required=False)

    def validate(self, attrs):
        contact = attrs.get('contact')
        сontact_type = attrs.get('contact_type')

        if not сontact_type:
            сontact_type = 'email' if '@' in contact else 'phone'

        if сontact_type == 'email':
            try:
                user = User.objects.get(email=contact)
            except User.DoesNotExist:
                raise serializers.ValidationError("Аккаунт с таким email не найден")
        else:
            normalized_phone = normalize_phone(contact)
            if not normalized_phone:
                raise serializers.ValidationError("Неверный формат телефона")

            try:
                user = User.objects.get(phone=normalized_phone)
            except User.DoesNotExist:
                raise serializers.ValidationError("Аккаунт с таким телефоном не найден")

        attrs['user'] = user
        return attrs

    def save(self):
        user = self.validated_data['user']
        # TODO: Отправка ссылки для сброса пароля на email пользователя
        # Всегда отправляем на email, так как email обязателен
        return {
            'message': 'Ссылка для сброса пароля отправлена на ваш email',
            'fallback': 'Если вы не получили письмо, позвоните нашему менеджеру по телефону +7-XXX-XXX-XX-XX'
        }


class PasswordResetConfirmSerializer(serializers.Serializer):
    uidb64 = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    new_password2 = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        new_password = attrs.get('new_password')
        new_password2 = attrs.get('new_password2')

        if new_password != new_password2:
            raise serializers.ValidationError({"new_password": "Пароли не совпадают"})

        try:
            uid = force_str(urlsafe_base64_decode(attrs['uidb64']))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError("Недействительная ссылка")

        if not default_token_generator.check_token(user, attrs['token']):
            raise serializers.ValidationError("Недействительная или просроченная ссылка")

        attrs['user'] = user
        return attrs

    def save(self):
        user = self.validated_data['user']
        user.set_password(self.validated_data['new_password'])
        user.save()
        return {'message': 'Пароль успешно изменен'}

class VerifyEmailSerializer(serializers.Serializer):
    pass

class VerifyEmailConfirmSerializer(serializers.Serializer):
    pass

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'phone', 'first_name', 'last_name', 'patronymic', 
                 'date_joined', 'is_email_verified']
        read_only_fields = ['id', 'email', 'date_joined', 'is_email_verified']

    def validate_phone(self, value):
        if value:
            normalized = normalize_phone(value)
            if not normalized:
                raise serializers.ValidationError("Неверный формат телефона")
            # Проверяем, что телефон не занят другим пользователем
            if User.objects.filter(phone=normalized).exclude(pk=self.instance.pk).exists():
                raise serializers.ValidationError("Этот телефон уже используется другим пользователем")
            return normalized
        return value




class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Кастомный serializer для JWT токенов"""
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        token['phone'] = user.phone
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name
        token['is_email_verified'] = user.is_email_verified
        return token
